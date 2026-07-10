"""
Tests for the ITES defence layer.
These tests exercise the mediator-backed ITES implementation:
- primitive proposals are declared when authorised,
- nested proposals are only allowed when the current influencers can read them,
- the defence returns a structured report.
"""
from __future__ import annotations
from dataclasses import dataclass
from fourth_year_project.core import Artifact, Principal, Provenance
from fourth_year_project.ites import Guarantee
from fourth_year_project.ites.reference import ReferenceITES
from fourth_year_project.sled.environment import Data
@dataclass(frozen=True, slots=True)
class PrimitiveProposal:
    action: str
@dataclass(frozen=True, slots=True)
class NestedProposal:
    inputs: frozenset[Data]
def test_reference_ites_declares_authorised_primitive_proposals() -> None:
    alice = Principal("alice", "Alice")
    initial_inputs = frozenset(
        {
            Artifact(
                value=Data(
                    authors=frozenset({alice}),
                    readers=frozenset({alice}),
                    tag="seed",
                ),
                provenance=Provenance.from_principal(alice),
            )
        }
    )
    seen_inputs: list[frozenset[Artifact[object]]] = []
    declared: list[object] = []
    def llm_call(inputs: frozenset[Artifact[object]]) -> frozenset[object]:
        seen_inputs.append(inputs)
        return frozenset({PrimitiveProposal(action="approve")})
    def declare(item: object) -> None:
        declared.append(item)
    defence = ReferenceITES(max_llm_calls=3)
    report = defence.run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=declare,
    )
    assert len(seen_inputs) == 1
    assert seen_inputs[0] == initial_inputs
    assert declared == [PrimitiveProposal(action="approve")]
    assert report.declared_actions == frozenset({PrimitiveProposal(action="approve")})
    assert report.blocked_actions == frozenset()
    assert all(isinstance(guarantee, Guarantee) for guarantee in report.guarantees)
def test_reference_ites_blocks_unreadable_nested_proposals() -> None:
    alice = Principal("alice", "Alice")
    bob = Principal("bob", "Bob")
    readable = Data(
        authors=frozenset({alice}),
        readers=frozenset({alice}),
        tag="readable",
    )
    unreadable = Data(
        authors=frozenset({bob}),
        readers=frozenset({bob}),
        tag="unreadable",
    )
    initial_inputs = frozenset(
        {
            Artifact(
                value=readable,
                provenance=Provenance.from_principal(alice),
            )
        }
    )
    declared: list[object] = []
    def llm_call(inputs: frozenset[Artifact[object]]) -> frozenset[object]:
        _ = inputs
        return frozenset(
            {
                NestedProposal(inputs=frozenset({readable})),
                NestedProposal(inputs=frozenset({unreadable})),
            }
        )
    def declare(item: object) -> None:
        declared.append(item)
    defence = ReferenceITES(max_llm_calls=3)
    report = defence.run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=declare,
    )
    assert NestedProposal(inputs=frozenset({readable})) in declared
    assert NestedProposal(inputs=frozenset({unreadable})) not in declared
    assert NestedProposal(inputs=frozenset({unreadable})) in report.blocked_actions
    assert NestedProposal(inputs=frozenset({readable})) in report.declared_actions
def test_reference_ites_records_configured_guarantees() -> None:
    alice = Principal("alice", "Alice")
    initial_inputs = frozenset(
        {
            Artifact(
                value=Data(
                    authors=frozenset({alice}),
                    readers=frozenset({alice}),
                    tag="seed",
                ),
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
