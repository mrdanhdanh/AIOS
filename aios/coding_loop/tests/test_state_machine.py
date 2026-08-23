"""Tests for the coding loop state machine (T145)."""

import pytest

from aios.coding_loop import (
    CodingLoopState,
    CodingLoopStateMachine,
    TRANSITIONS,
)
from aios.coding_loop._common import CodingLoopError


def test_immutable_loop_id():
    sm = CodingLoopStateMachine(loop_id="loop1", policy_ref="pol1")
    assert sm.loop_id == "loop1"
    assert sm.current_state == CodingLoopState.OBSERVING


def test_transition_with_artifact_advances():
    sm = CodingLoopStateMachine(policy_ref="pol1")
    nxt = sm.transition("observe-artifact", policy_ref="pol1")
    assert nxt == CodingLoopState.CLASSIFYING
    assert sm.current_state == CodingLoopState.CLASSIFYING


def test_transition_missing_artifact_rejected():
    sm = CodingLoopStateMachine(policy_ref="pol1")
    with pytest.raises(CodingLoopError):
        sm.transition("")  # fail-closed: artifact required


def test_transition_missing_policy_rejected():
    sm = CodingLoopStateMachine()  # no policy_ref
    with pytest.raises(CodingLoopError):
        sm.transition("observe-artifact")  # fail-closed: policy required


def test_deterministic_next_state():
    # Same state -> same next state (deterministic).
    assert CodingLoopStateMachine().next_state(CodingLoopState.OBSERVING) == CodingLoopState.CLASSIFYING
    assert CodingLoopStateMachine().next_state(CodingLoopState.DIAGNOSING) == CodingLoopState.REPAIRING
    assert TRANSITIONS[CodingLoopState.SAFETY] == CodingLoopState.DONE


def test_transition_history_recorded():
    sm = CodingLoopStateMachine(policy_ref="pol1")
    sm.transition("a", policy_ref="pol1")
    sm.transition("b", policy_ref="pol1")
    assert len(sm.transition_history) == 2
    assert sm.transition_history[0].from_state == CodingLoopState.OBSERVING


def test_provenance_hash_present():
    sm = CodingLoopStateMachine(loop_id="loop1", policy_ref="pol1")
    prov = sm.provenance()
    assert prov["loop_id"] == "loop1"
    assert prov["content_hash"]
    assert prov["authority"] == "aios"
