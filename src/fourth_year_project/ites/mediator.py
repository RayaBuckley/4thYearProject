"""
Core ITES mediation algorithm.
This module contains the executable heart of ITES.
The mediator:
- tracks provenance-derived influence through nested LLM calls,
- only allows nested execution when the current influencers can read the inputs,
- allows primitive actions only when the configured primitive authoriser permits them,
- returns a structured report of the run.
This is the first place where the old exploratory evaluator becomes a maintainable
defence kernel.
"""
from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Callable, FrozenSet
from fourth_year_project.core import Artifact, Principal, Provenance
from . import Declare, Guarantee, ITES, ITESReport, LLMCall
PrimitiveAuthoriser = Callable[[str, FrozenSet[Principal]], bool]
NestedAuthoriser = Callable[[Any, FrozenSet[Principal], FrozenSet[Any]], bool]
def _default_primitive_authoriser(action: str, influencers: FrozenSet[Principal]) -> bool:
    """
    Default primitive action policy.
    The current project does not yet have a fully wired action-permission model,
    so the default is permissive. The hook exists so a later policy layer can be
    attached without changing the mediator.
    """
    _ = action
    _ = influencers
    return True
def _default_nested_authoriser(
    environment: Any,
    influencers: FrozenSet[Principal],
    inputs: FrozenSet[Any],
) -> bool:
    """
    Default nested execution policy.
    A nested LLM call is permitted only when every current influencer can read
    every proposed input. This is the core safety rule inherited from the
    previous codebase.
    """
    _ = environment
    for item in inputs:
        readers = frozenset(getattr(item, "readers", frozenset()))
        if not all(principal in readers for principal in influencers):
            return False
    return True
def _artifact_principals(inputs: Iterable[Artifact[Any]]) -> FrozenSet[Principal]:
    """
    Extract the union of principals appearing in artifact provenance.
    """
    principals: set[Principal] = set()
    for artifact in inputs:
        principals.update(artifact.provenance.principals)
    return frozenset(principals)
def _provenance_for_input(item: Any) -> Provenance:
    """
    Build provenance for a raw SLED input item.
    The provenance is derived from the item's authors, then tagged as an input
    originating from the SLED environment.
    """
    provenance = Provenance()
    for author in getattr(item, "authors", frozenset()):
        provenance = provenance.merge(Provenance.from_principal(author))
    return provenance.with_operation("sled_input")
def _materialise_inputs(inputs: FrozenSet[Any]) -> FrozenSet[Artifact[Any]]:
    """
    Convert raw SLED inputs into provenance-bearing artifacts.
    """
    return frozenset(
        Artifact(value=item, provenance=_provenance_for_input(item))
        for item in inputs
    )
@dataclass(frozen=True, slots=True)
class MediatingITES(ITES):
    """
    Reference mediator for provenance-aware defence execution.
    Parameters
    ----------
    max_llm_calls:
        Maximum number of model invocations permitted along a single branch.
        The initial call counts as one invocation.
    primitive_authoriser:
        Hook for checking whether a primitive action is allowed for the current
        influence set.
    nested_authoriser:
        Hook for checking whether a nested LLM execution request is allowed.
        The default rule enforces readability of the requested inputs by all
        current influencers.
    """
    max_llm_calls: int = 3
    primitive_authoriser: PrimitiveAuthoriser = _default_primitive_authoriser
    nested_authoriser: NestedAuthoriser = _default_nested_authoriser
    def __post_init__(self) -> None:
        if self.max_llm_calls < 1:
            raise ValueError("max_llm_calls must be at least 1")
    def run(
        self,
        environment: Any,
        initial_inputs: FrozenSet[Artifact[Any]],
        llm_call: LLMCall,
        declare: Declare,
    ) -> ITESReport:
        declared_actions: set[Any] = set()
        blocked_actions: set[Any] = set()
        llm_calls_used = 0
        nested_inputs_readable = True
        primitive_actions_authorised = True
        initial_influencers = _artifact_principals(initial_inputs)
        def descend(
            inputs: FrozenSet[Artifact[Any]],
            influencers: FrozenSet[Principal],
            depth: int,
        ) -> None:
            nonlocal llm_calls_used
            nonlocal nested_inputs_readable
            nonlocal primitive_actions_authorised
            if depth > self.max_llm_calls:
                return
            llm_calls_used += 1
            proposals = llm_call(inputs)
            for proposal in proposals:
                if hasattr(proposal, "inputs"):
                    raw_inputs = frozenset(getattr(proposal, "inputs"))
                    if depth >= self.max_llm_calls:
                        nested_inputs_readable = False
                        blocked_actions.add(proposal)
                        continue
                    if not self.nested_authoriser(environment, influencers, raw_inputs):
                        nested_inputs_readable = False
                        blocked_actions.add(proposal)
                        continue
                    declare(proposal)
                    declared_actions.add(proposal)
                    nested_artifacts = _materialise_inputs(raw_inputs)
                    next_influencers = influencers | _artifact_principals(nested_artifacts)
                    descend(nested_artifacts, next_influencers, depth + 1)
                    continue
                if hasattr(proposal, "action"):
                    action = getattr(proposal, "action")
                    if not self.primitive_authoriser(action, influencers):
                        primitive_actions_authorised = False
                        blocked_actions.add(proposal)
                        continue
                    declare(proposal)
                    declared_actions.add(proposal)
                    continue
                blocked_actions.add(proposal)
        descend(initial_inputs, initial_influencers, 1)
        guarantees = frozenset(
            {
                Guarantee(
                    name="bounded_llm_calls",
                    holds=llm_calls_used <= self.max_llm_calls,
                    details=(
                        f"Used {llm_calls_used} LLM call(s) with limit "
                        f"{self.max_llm_calls}."
                    ),
                ),
                Guarantee(
                    name="nested_inputs_readable",
                    holds=nested_inputs_readable,
                    details=(
                        "Every nested execution request satisfied the readability "
                        "check for the current influencers."
                    ),
                ),
                Guarantee(
                    name="primitive_actions_authorised",
                    holds=primitive_actions_authorised,
                    details=(
                        "Every primitive action satisfied the configured "
                        "primitive authoriser."
                    ),
                ),
            }
        )
        return ITESReport(
            guarantees=guarantees,
            declared_actions=frozenset(declared_actions),
            blocked_actions=frozenset(blocked_actions),
        )
__all__ = [
    "MediatingITES",
]
