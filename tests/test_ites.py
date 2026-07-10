"""
Tests for the ITES defence layer.
These tests ensure the reference defence behaves like a stable executable
surface: it accepts an environment, forwards the initial artefacts to the LLM,
declares proposals, and returns a structured report.
"""
from __future__ import annotations
from collections.abc import Callable
from fourth_year_project.core import Artifact, Principal, Provenance
from fourth_year_project.ites import Guarantee
from fourth_year_project.ites.reference import ReferenceITES
def test_reference_ites_declares_llm_proposals() -> None:
    alice = Principal("alice", "Alice")
    initial_inputs = frozenset(
        {
            Artifact(
                value="hello",
                provenance=Provenance.from_principal(alice),
            )
        }
    )
    seen_inputs: list[frozenset[Artifact[object]]] = []
    declared: list[object] = []
    def llm_call(inputs: frozenset[Artifact[object]]) -> frozenset[object]:
        seen_inputs.append(inputs)
        return frozenset({"primitive-action", "nested-task"})
    def declare(item: object) -> None:
        declared.append(item)
    defence = ReferenceITES()
    report = defence.run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=declare,
    )
    assert len(seen_inputs) == 1
    assert seen_inputs[0] == initial_inputs
    assert set(declared) == {"primitive-action", "nested-task"}
    assert report.declared_actions == frozenset({"primitive-action", "nested-task"})
    assert report.blocked_actions == frozenset()
    assert report.guarantees == frozenset()
def test_reference_ites_records_configured_guarantees() -> None:
    alice = Principal("alice", "Alice")
    initial_inputs = frozenset(
        {
            Artifact(
                value="hello",
                provenance=Provenance.from_principal(alice),
            )
        }
    )
    def llm_call(inputs: frozenset[Artifact[object]]) -> frozenset[object]:
        _ = inputs
        return frozenset()
    declared: list[object] = []
    def declare(item: object) -> None:
        declared.append(item)
    defence = ReferenceITES(guarantees=frozenset({"no_unauthorised_action"}))
    report = defence.run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=declare,
    )
    assert declared == []
    assert report.guarantees == frozenset(
        {
            Guarantee(
                name="no_unauthorised_action",
                holds=True,
                details="Guarantee recorded by reference ITES run.",
            )
        }
    )
