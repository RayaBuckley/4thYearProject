"""
Tests for ITES execution state.

These tests lock in the immutability and trace semantics of the execution
state object used by the mediator.
"""

from __future__ import annotations

from conflux.core import Artifact, Principal, Provenance
from conflux.ites import Guarantee
from conflux.ites.state import ExecutionState, ExecutionStep


def test_can_call_llm_respects_budget() -> None:
    state = ExecutionState(environment=object(), max_llm_calls=2)

    assert state.can_call_llm() is True
    state = state.increment_llm_calls()
    assert state.can_call_llm() is True
    state = state.increment_llm_calls()
    assert state.can_call_llm() is False


def test_recorded_actions_do_not_mutate_original_state() -> None:
    state = ExecutionState(environment=object())

    declared_state = state.record_declared("allow")
    blocked_state = state.record_blocked("deny")

    assert state.declared_actions == frozenset()
    assert state.blocked_actions == frozenset()
    assert declared_state.declared_actions == frozenset({"allow"})
    assert blocked_state.blocked_actions == frozenset({"deny"})


def test_add_guarantee_returns_new_state() -> None:
    state = ExecutionState(environment=object())
    guarantee = Guarantee(name="bounded_llm_calls", holds=True)

    updated = state.add_guarantee(guarantee)

    assert state.guarantees == frozenset()
    assert updated.guarantees == frozenset({guarantee})


def test_add_step_appends_to_trace_without_mutating_original() -> None:
    alice = Principal("alice", "Alice")
    artifact = Artifact(
        value="hello",
        provenance=Provenance.from_principal(alice),
    )
    state = ExecutionState(environment=object(), active_influencers=frozenset({alice}))

    step = ExecutionStep(
        depth=1,
        inputs=frozenset({artifact}),
        proposals=frozenset({"proposal"}),
        declared=frozenset({"proposal"}),
        blocked=frozenset(),
        influencers=frozenset({alice}),
        note="initial step",
    )

    updated = state.add_step(step)

    assert state.trace.steps == ()
    assert updated.trace.steps == (step,)
    assert updated.trace.last() == step


def test_with_influencers_returns_new_state() -> None:
    alice = Principal("alice", "Alice")
    bob = Principal("bob", "Bob")
    state = ExecutionState(environment=object(), active_influencers=frozenset({alice}))

    updated = state.with_influencers(frozenset({alice, bob}))

    assert state.active_influencers == frozenset({alice})
    assert updated.active_influencers == frozenset({alice, bob})
