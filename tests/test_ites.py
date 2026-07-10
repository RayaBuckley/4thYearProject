"""
Tests for the ITES defence layer.

These tests exercise the mediator-backed ITES implementation and verify the
observable behaviour of the defence. The internal implementation may evolve,
but these behavioural guarantees should remain stable.
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


def _initial_inputs() -> tuple[Principal, frozenset[Artifact[Data]]]:
    alice = Principal("alice", "Alice")

    seed = Data(
        authors=frozenset({alice}),
        readers=frozenset({alice}),
        tag="seed",
    )

    artifacts = frozenset(
        {
            Artifact(
                value=seed,
                provenance=Provenance.from_principal(alice),
            )
        }
    )

    return alice, artifacts


def test_reference_ites_declares_authorised_primitive_proposals() -> None:
    _, initial_inputs = _initial_inputs()

    llm_inputs: list[frozenset[Artifact[object]]] = []
    declared: list[object] = []

    def llm_call(
        inputs: frozenset[Artifact[object]],
    ) -> frozenset[object]:
        llm_inputs.append(inputs)
        return frozenset(
            {
                PrimitiveProposal(action="approve"),
            }
        )

    def declare(item: object) -> None:
        declared.append(item)

    report = ReferenceITES().run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=declare,
    )

    assert len(llm_inputs) == 1
    assert llm_inputs[0] == initial_inputs

    proposal = PrimitiveProposal(action="approve")

    assert declared == [proposal]
    assert report.declared_actions == frozenset({proposal})
    assert report.blocked_actions == frozenset()

    guarantee_names = {g.name for g in report.guarantees}

    assert guarantee_names == {
        "bounded_llm_calls",
        "nested_inputs_readable",
        "primitive_actions_authorised",
    }


def test_reference_ites_blocks_unreadable_nested_execution() -> None:
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

    def llm_call(
        inputs: frozenset[Artifact[object]],
    ) -> frozenset[object]:
        _ = inputs
        return frozenset(
            {
                NestedProposal(inputs=frozenset({readable})),
                NestedProposal(inputs=frozenset({unreadable})),
            }
        )

    def declare(item: object) -> None:
        declared.append(item)

    report = ReferenceITES().run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=declare,
    )

    allowed = NestedProposal(inputs=frozenset({readable}))
    blocked = NestedProposal(inputs=frozenset({unreadable}))

    assert allowed in report.declared_actions
    assert blocked in report.blocked_actions

    nested_guarantee = next(
        g
        for g in report.guarantees
        if g.name == "nested_inputs_readable"
    )

    assert nested_guarantee.holds is False


def test_reference_ites_respects_llm_budget() -> None:
    _, initial_inputs = _initial_inputs()

    calls = 0

    def llm_call(
        inputs: frozenset[Artifact[object]],
    ) -> frozenset[object]:
        nonlocal calls
        _ = inputs
        calls += 1

        return frozenset(
            {
                PrimitiveProposal(action=f"action-{calls}"),
            }
        )

    report = ReferenceITES(max_llm_calls=1).run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=lambda _: None,
    )

    assert calls == 1

    budget = next(
        g
        for g in report.guarantees
        if g.name == "bounded_llm_calls"
    )

    assert budget.holds is True


def test_reference_ites_is_deterministic() -> None:
    _, initial_inputs = _initial_inputs()

    def llm_call(
        inputs: frozenset[Artifact[object]],
    ) -> frozenset[object]:
        _ = inputs
        return frozenset(
            {
                PrimitiveProposal(action="approve"),
            }
        )

    report_one = ReferenceITES().run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=lambda _: None,
    )

    report_two = ReferenceITES().run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=llm_call,
        declare=lambda _: None,
    )

    assert report_one == report_two


def test_report_contains_guarantees() -> None:
    _, initial_inputs = _initial_inputs()

    report = ReferenceITES().run(
        environment=object(),
        initial_inputs=initial_inputs,
        llm_call=lambda _: frozenset(),
        declare=lambda _: None,
    )

    assert all(isinstance(g, Guarantee) for g in report.guarantees)
    assert len(report.guarantees) == 3
