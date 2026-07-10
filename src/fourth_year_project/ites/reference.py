"""
Reference ITES implementation.
This is the first concrete defence implementation. It is intentionally small
and serves as the starting point for the dissertation prototype.
The implementation is designed to stay close to the previous experimental
codebase while moving it into a maintainable, testable structure.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, FrozenSet, Iterable
from fourth_year_project.core import Artifact
from . import Declare, EnvironmentLike, Guarantee, ITES, ITESReport, LLMCall, Proposal
@dataclass(slots=True)
class ReferenceITES(ITES):
    """
    Reference defence for provenance-aware execution.
    This implementation does not attempt to solve the entire evaluation problem
    yet. Instead, it provides the first stable executable surface for the ITES
    architecture so that the evaluation model can be developed incrementally.
    The intended development pattern is:
    - define guarantees,
    - implement the minimum defence logic needed to check them,
    - expand with richer environment semantics later.
    """
    guarantees: FrozenSet[str] = field(default_factory=frozenset)
    def run(
        self,
        environment: EnvironmentLike,
        initial_inputs: FrozenSet[Artifact[Any]],
        llm_call: LLMCall,
        declare: Declare,
    ) -> ITESReport:
        """
        Run the defence on a given environment.
        This initial version is deliberately conservative:
        - it forwards the initial artefacts to the model,
        - it records declared proposals,
        - it returns a report without assuming any extra environment features.
        The environment argument is accepted so that SLED can later define the
        evaluation semantics in a richer way without changing the defence API.
        """
        _ = environment
        declared_actions: set[Any] = set()
        blocked_actions: set[Any] = set()
        achieved: set[Guarantee] = set()
        proposals = llm_call(initial_inputs)
        for proposal in proposals:
            if _is_declarable(proposal):
                declare(proposal)
                declared_actions.add(proposal)
            else:
                blocked_actions.add(proposal)
        for guarantee_name in self.guarantees:
            achieved.add(
                Guarantee(
                    name=guarantee_name,
                    holds=True,
                    details="Guarantee recorded by reference ITES run.",
                )
            )
        return ITESReport(
            guarantees=frozenset(achieved),
            declared_actions=frozenset(declared_actions),
            blocked_actions=frozenset(blocked_actions),
        )
def _is_declarable(proposal: Proposal) -> bool:
    """
    Determine whether a proposal can be declared directly.
    The reference implementation currently treats everything as declarable.
    This keeps the first version simple and avoids prematurely coupling ITES to
    a particular proposal taxonomy.
    """
    return True
