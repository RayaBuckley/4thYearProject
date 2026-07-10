"""
SLED evaluator.
This module runs an ITES defence against a constructed environment and records
whether the defence behaved safely.
The evaluator is intentionally lightweight at this stage: it is a harness for
replaying a scenario, not a full combinatorial exploration engine. That keeps it
maintainable while the project is still being shaped.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, Iterable
from fourth_year_project.core import Artifact, Principal, Provenance
from fourth_year_project.ites import ITES, ITESReport
from .environment import Data, Environment, Proposal
LLMCall = Callable[[FrozenSet[Artifact[Any]]], FrozenSet[Proposal]]
Declare = Callable[[Any], None]
@dataclass(slots=True)
class EvaluationResult:
    """
    Outcome of an evaluation run.
    Attributes
    ----------
    report:
        The report returned by ITES.
    llm_inputs:
        The sequence of artefact sets passed to the model.
    declared:
        The proposals that were declared during the run.
    """
    report: ITESReport
    llm_inputs: list[FrozenSet[Artifact[Any]]] = field(default_factory=list)
    declared: list[Any] = field(default_factory=list)
@dataclass(slots=True)
class Evaluator:
    """
    Run an ITES defence against a SLED environment.
    """
    environment: Environment
    defence: ITES
    llm_call: LLMCall
    def run(self, initial_inputs: Iterable[Data]) -> EvaluationResult:
        """
        Run the defence on the selected initial inputs.
        """
        selected_inputs = frozenset(initial_inputs)
        input_artifacts = frozenset(
            Artifact(
                value=item,
                provenance=self._provenance_for(item),
            )
            for item in selected_inputs
        )
        llm_inputs: list[FrozenSet[Artifact[Any]]] = []
        declared: list[Any] = []
        def tracked_llm_call(inputs: FrozenSet[Artifact[Any]]) -> FrozenSet[Proposal]:
            llm_inputs.append(inputs)
            return self.llm_call(inputs)
        def tracked_declare(item: Any) -> None:
            declared.append(item)
        report = self.defence.run(
            environment=self.environment,
            initial_inputs=input_artifacts,
            llm_call=tracked_llm_call,
            declare=tracked_declare,
        )
        return EvaluationResult(
            report=report,
            llm_inputs=llm_inputs,
            declared=declared,
        )
    def _provenance_for(self, item: Data) -> Provenance:
        """
        Construct provenance for an environment item.
        """
        provenance = Provenance()
        for author in item.authors:
            provenance = provenance.merge(Provenance.from_principal(author))
        provenance = provenance.with_operation("sled_environment_input")
        return provenance
