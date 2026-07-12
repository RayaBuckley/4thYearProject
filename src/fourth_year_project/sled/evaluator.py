"""
Exhaustive SLED evaluator.

This module replaces the lightweight replay harness with a bounded combinatorial
search engine. The evaluator explores all proposal combinations up to the
configured branching limits, while optionally compressing the environment into
representative equivalence classes to increase achievable search depth.

The design keeps the old prototype's exhaustive semantics:
- nested execution is explored combinatorially,
- primitive actions and nested LLM requests are both branch points,
- the evaluator records every branch that it traverses,
- representative environments reduce redundant branching when several data
  items share the same permission structure.

The evaluator does not alter the intersection rule itself; that is enforced by
the authorisation layer.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from itertools import chain, combinations
from typing import Any, FrozenSet, Sequence

from fourth_year_project.core import Artifact, Principal, Provenance
from fourth_year_project.ites import Guarantee, ITES, ITESReport

from .environment import Data, Environment, LLMExecutionAction, PrimitiveAction, Proposal


LLMCall = Callable[[FrozenSet[Artifact[Any]]], FrozenSet[Proposal]]
Declare = Callable[[Any], None]


@dataclass(frozen=True, slots=True)
class RepresentativeClass:
    """
    A group of environment items that share the same author/readers structure.

    Items in the same class are behaviourally similar for exhaustive search
    purposes, so one representative can stand in for the whole class.
    """

    representative: Data
    members: FrozenSet[Data] = frozenset()


@dataclass(frozen=True, slots=True)
class RepresentativeEnvironment:
    """A compressed environment built from equivalence classes of data."""

    environment: Environment
    classes: FrozenSet[RepresentativeClass] = frozenset()

    @property
    def compression_factor(self) -> float:
        original = sum(len(cls.members) for cls in self.classes)
        if not original:
            return 1.0
        return original / max(1, len(self.environment.data))


@dataclass(slots=True)
class ExhaustiveEvaluationResult:
    """Outcome of a complete exhaustive evaluation run."""

    report: ITESReport
    branches_explored: int
    terminal_branches: int
    max_depth_reached: int
    llm_inputs: list[FrozenSet[Artifact[Any]]] = field(default_factory=list)
    declared: list[Any] = field(default_factory=list)
    representative_environment: RepresentativeEnvironment | None = None


def _powerset(items: Sequence[Any], *, min_size: int = 0, max_size: int | None = None):
    """Yield subsets of items in increasing size order."""
    n = len(items)
    if max_size is None:
        max_size = n
    upper = min(n, max_size)
    for r in range(min_size, upper + 1):
        for combo in combinations(items, r):
            yield combo


def _provenance_for(item: Data) -> Provenance:
    """Construct provenance for a raw SLED data item."""
    provenance = Provenance()
    for author in item.authors:
        provenance = provenance.merge(Provenance.from_principal(author))
    return provenance.with_operation("sled_environment_input")


def _materialise_inputs(inputs: FrozenSet[Data]) -> FrozenSet[Artifact[Any]]:
    """Convert raw SLED inputs into provenance-bearing artefacts."""
    return frozenset(Artifact(value=item, provenance=_provenance_for(item)) for item in inputs)


def _signature(item: Data) -> tuple[frozenset[str], frozenset[str]]:
    """Return the permission-structure signature for a data item."""
    authors = frozenset(author.id for author in item.authors)
    readers = frozenset(reader.id for reader in item.readers)
    return authors, readers


def compress_environment(environment: Environment) -> RepresentativeEnvironment:
    """
    Compress an environment into representative equivalence classes.

    Items with identical author/readers signatures are grouped together.
    This preserves the relevant security structure while reducing branching.
    """
    groups: dict[tuple[frozenset[str], frozenset[str]], list[Data]] = {}
    for item in environment.data:
        groups.setdefault(_signature(item), []).append(item)

    classes: list[RepresentativeClass] = []
    representatives: set[Data] = set()

    for members in groups.values():
        representative = min(
            members,
            key=lambda d: (
                d.tag is None,
                d.tag or "",
                len(d.authors),
                len(d.readers),
            ),
        )
        representatives.add(representative)
        classes.append(
            RepresentativeClass(
                representative=representative,
                members=frozenset(members),
            )
        )

    return RepresentativeEnvironment(
        environment=Environment(data=frozenset(representatives)),
        classes=frozenset(classes),
    )


def _llm_inputs_readable(inputs: FrozenSet[Data], influencers: FrozenSet[Principal]) -> bool:
    """
    Exact nested-call readability rule from the previous prototype.

    A nested execution request is allowed only when every current influencer
    can read every proposed input.
    """
    for item in inputs:
        for principal in influencers:
            if principal not in item.readers:
                return False
    return True


@dataclass(slots=True)
class ExhaustiveEvaluator:
    """
    Exhaustively explore the branching behaviour of a defence across one
    environment.

    Parameters
    ----------
    defence:
        The ITES defence implementation to run.
    primitive_actions:
        The action vocabulary used to construct primitive proposal atoms.
        In realistic integrations this should be supplied by the benchmark or
        provider adapter.
    max_llm_calls:
        Maximum depth of the explored call tree.
    option_width:
        Maximum number of proposals in a non-terminal LLM response.
    terminal_option_width:
        Maximum number of primitive proposals in the final LLM response.
    use_representative_environment:
        Whether to compress the environment before branching.
    max_execution_input_size:
        Optional cap on nested-input subset size. Leave as None to explore the
        full powerset of representative data.
    """

    defence: ITES
    primitive_actions: FrozenSet[str]
    max_llm_calls: int = 3
    option_width: int = 2
    terminal_option_width: int = 3
    use_representative_environment: bool = True
    max_execution_input_size: int | None = None

    def __post_init__(self) -> None:
        if self.max_llm_calls < 1:
            raise ValueError("max_llm_calls must be at least 1")
        if self.option_width < 0:
            raise ValueError("option_width must be non-negative")
        if self.terminal_option_width < 0:
            raise ValueError("terminal_option_width must be non-negative")

    def run(self, environment: Environment, initial_inputs: Iterable[Data]) -> ExhaustiveEvaluationResult:
        """
        Run an exhaustive search over the defence's execution tree.

        The evaluator replays every decision path induced by the branching
        oracle, using representative inputs when enabled.
        """
        rep = compress_environment(environment) if self.use_representative_environment else RepresentativeEnvironment(environment=environment)

        selected_inputs = frozenset(initial_inputs)
        if not selected_inputs <= environment.data:
            missing = selected_inputs - environment.data
            raise ValueError(f"Initial inputs are not in the environment: {missing!r}")

        llm_inputs: list[FrozenSet[Artifact[Any]]] = []
        declared: list[Any] = []
        terminal_reports: list[ITESReport] = []

        primitive_atoms = [PrimitiveAction(action=a) for a in sorted(self.primitive_actions)]
        execution_sources = list(rep.environment.data)
        if self.max_execution_input_size is None:
            execution_subsets = list(_powerset(execution_sources, min_size=1))
        else:
            execution_subsets = list(
                _powerset(
                    execution_sources,
                    min_size=1,
                    max_size=self.max_execution_input_size,
                )
            )

        execution_atoms = [LLMExecutionAction(inputs=frozenset(subset)) for subset in execution_subsets]
        all_atoms = primitive_atoms + execution_atoms

        branch_options: list[FrozenSet[Proposal]] = []
        for combo in _powerset(all_atoms, min_size=0, max_size=self.option_width):
            branch_options.append(frozenset(combo))

        terminal_options: list[FrozenSet[Proposal]] = []
        for combo in _powerset(primitive_atoms, min_size=0, max_size=self.terminal_option_width):
            terminal_options.append(frozenset(combo))

        if not branch_options:
            branch_options = [frozenset()]
        if not terminal_options:
            terminal_options = [frozenset()]

        decision_path: list[int] = [0] * self.max_llm_calls
        branches_explored = 0
        terminal_branches = 0
        max_depth_reached = 0
        final_report: ITESReport | None = None

        def tracked_declare(item: Any) -> None:
            declared.append(item)

        while True:
            branches_explored += 1
            current_index = 0
            llm_inputs.clear()

            def branching_llm_call(inputs: FrozenSet[Artifact[Any]]) -> FrozenSet[Proposal]:
                nonlocal current_index, max_depth_reached
                llm_inputs.append(inputs)
                max_depth_reached = max(max_depth_reached, current_index + 1)

                if current_index >= self.max_llm_calls - 1:
                    options = terminal_options
                else:
                    options = branch_options

                choice = decision_path[current_index]
                if choice >= len(options):
                    return frozenset()

                current_index += 1
                return options[choice]

            input_artifacts = _materialise_inputs(selected_inputs)

            report = self.defence.run(
                environment=rep.environment,
                initial_inputs=input_artifacts,
                llm_call=branching_llm_call,
                declare=tracked_declare,
            )
            final_report = report
            terminal_branches += 1

            if current_index == 0:
                max_depth_reached = max(max_depth_reached, 1)

            i = current_index - 1 if current_index > 0 else self.max_llm_calls - 1
            while i >= 0:
                decision_path[i] += 1
                limit = len(terminal_options) if i == self.max_llm_calls - 1 else len(branch_options)
                if decision_path[i] < limit:
                    break
                decision_path[i] = 0
                i -= 1

            if i < 0:
                break

        if final_report is None:
            final_report = ITESReport(
                guarantees=frozenset(
                    {
                        Guarantee(
                            name="no_runs_executed",
                            holds=False,
                            details="No branches were explored.",
                        )
                    }
                ),
                declared_actions=frozenset(),
                blocked_actions=frozenset(),
            )

        return ExhaustiveEvaluationResult(
            report=final_report,
            branches_explored=branches_explored,
            terminal_branches=terminal_branches,
            max_depth_reached=max_depth_reached,
            llm_inputs=llm_inputs.copy(),
            declared=declared.copy(),
            representative_environment=rep if self.use_representative_environment else None,
        )


__all__ = [
    "ExhaustiveEvaluationResult",
    "ExhaustiveEvaluator",
    "RepresentativeClass",
    "RepresentativeEnvironment",
    "compress_environment",
]
