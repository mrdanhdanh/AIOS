"""Controller tests for Kill Switch (TASK-068).

Covers every Acceptance Criterion and Test Matrix row:
- manual halt -> all loops stop fail-closed
- policy halt -> correct scope
- halt mid in-flight -> drain + persist
- layer cố skip halt -> blocked fail-closed
- halt ghi audit -> provenance đầy đủ
- cùng halt signal + state -> cùng hành vi (deterministic)
- verified state not destroyed (durable)
"""

from __future__ import annotations

import pytest

from aios.kill_switch.contracts import (
    HaltScope,
    HaltSignal,
    HaltSource,
    HaltViolation,
)
from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.tests.conftest import (
    FailingDrainContext,
    FakeContext,
    make_signal,
)


# --- AC1: manual halt -> all loops stop fail-closed ---------------------- #
def test_manual_global_halt_stops_all_contexts_fail_closed():
    c = KillSwitchController()
    loop1 = FakeContext("loop-1", "loop")
    loop2 = FakeContext("loop-2", "loop")
    goal1 = FakeContext("goal-1", "goal")
    c.register(loop1)
    c.register(loop2)
    c.register(goal1)

    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "operator pressed stop")
    res = c.issue(sig)

    assert res.halted is True
    assert set(res.affected_contexts) == {"loop-1", "loop-2", "goal-1"}
    # every layer reports halted
    assert loop1.is_halted() and loop2.is_halted() and goal1.is_halted()
    # authoritative query
    assert c.is_halted() is True
    # no new action may start
    with pytest.raises(HaltViolation):
        c.begin_action("loop-1")


# --- AC1/AC6: policy halt -> correct scope ------------------------------- #
def test_policy_goal_scoped_halt_only_target():
    c = KillSwitchController()
    goal1 = FakeContext("goal-1", "goal")
    goal2 = FakeContext("goal-2", "goal")
    loop1 = FakeContext("loop-1", "loop")
    c.register(goal1)
    c.register(goal2)
    c.register(loop1)

    sig = make_signal(HaltSource.POLICY, HaltScope.GOAL, "policy violation", target_id="goal-1")
    c.issue(sig)

    assert c.is_halted(HaltScope.GOAL, "goal-1") is True
    assert c.is_halted(HaltScope.GOAL, "goal-2") is False
    assert c.is_halted(HaltScope.LOOP, "loop-1") is False
    assert goal1.is_halted() is True
    assert goal2.is_halted() is False
    assert loop1.is_halted() is False
    # non-target contexts may still act
    c.begin_action("goal-2", HaltScope.GOAL, "goal-2")


def test_safety_source_halt_works():
    c = KillSwitchController()
    loop1 = FakeContext("loop-1", "loop")
    c.register(loop1)
    sig = make_signal(HaltSource.SAFETY, HaltScope.GLOBAL, "safety threshold breached")
    res = c.issue(sig)
    assert res.halted is True
    assert loop1.is_halted()


# --- AC3: halt mid in-flight -> drain + persist -------------------------- #
def test_halt_mid_inflight_drains_and_persists():
    c = KillSwitchController()
    loop1 = FakeContext("loop-1", "loop", in_flight={"step": 7, "data": "x"})
    c.register(loop1)

    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    res = c.issue(sig)

    assert loop1.drain_called is True
    assert "loop-1" in res.drained_contexts
    # in-flight state persisted (durable)
    persisted = c.persistence().get_state("loop-1")
    assert persisted["in_flight"] == {"step": 7, "data": "x"}
    # no new action may start after drain
    with pytest.raises(HaltViolation):
        c.begin_action("loop-1")


# --- AC7: layer cố skip halt -> blocked fail-closed --------------------- #
def test_layer_that_skips_halt_is_blocked_fail_closed():
    c = KillSwitchController()
    compliant = FakeContext("loop-1", "loop")
    skipper = FakeContext("loop-2", "loop", skip=True)  # ignores halt
    c.register(compliant)
    c.register(skipper)

    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    with pytest.raises(HaltViolation):
        c.issue(sig)

    # Even though the skipper ignored the signal, the authoritative state is
    # halted (fail-closed) and blocks all new actions.
    assert c.is_halted() is True
    with pytest.raises(HaltViolation):
        c.begin_action("loop-2")
    # the skip was recorded as a violation
    assert any("did not halt" in str(v) for v in c.violations())


def test_failing_drain_does_not_break_fail_closed():
    c = KillSwitchController()
    bad = FailingDrainContext("loop-1", "loop")
    c.register(bad)
    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    with pytest.raises(HaltViolation):
        c.issue(sig)
    assert c.is_halted() is True


# --- AC4: halt ghi audit -> provenance đầy đủ --------------------------- #
def test_halt_writes_auditable_evidence_with_provenance():
    c = KillSwitchController()
    loop1 = FakeContext("loop-1", "loop")
    c.register(loop1)

    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    res = c.issue(sig)

    assert res.evidence_ref
    assert sig.evidence_ref == res.evidence_ref
    # provenance chain is complete (Rule 5)
    assert c._audit.provenance_complete(res.evidence_ref) is True


# --- AC5: deterministic — same signal + state -> same behavior --------- #
def test_same_signal_is_deterministic_and_idempotent():
    c = KillSwitchController()
    loop1 = FakeContext("loop-1", "loop")
    c.register(loop1)

    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    r1 = c.issue(sig)
    # issue the exact same signal again
    r2 = c.issue(sig)

    assert r1.signal_id == r2.signal_id
    assert r1.affected_contexts == r2.affected_contexts
    assert r1.evidence_ref == r2.evidence_ref
    assert r1.drained_contexts == r2.drained_contexts


def test_two_controllers_same_state_same_result():
    def build():
        c = KillSwitchController()
        c.register(FakeContext("loop-1", "loop"))
        c.register(FakeContext("goal-1", "goal"))
        return c

    c1, c2 = build(), build()
    sig = make_signal(HaltSource.POLICY, HaltScope.GLOBAL, "stop")
    r1, r2 = c1.issue(sig), c2.issue(sig)
    assert r1.affected_contexts == r2.affected_contexts
    assert r1.evidence_ref == r2.evidence_ref


# --- AC2: verified state not destroyed (durable) ------------------------ #
def test_verified_state_survives_halt_and_drain():
    c = KillSwitchController()
    loop1 = FakeContext("loop-1", "loop", in_flight={"wip": 1})
    c.register(loop1)

    # a verified state exists before the halt
    c.persistence().persist_verified("goal-1", {"status": "verified", "hash": "abc"})
    assert c.persistence().get_verified("goal-1")["status"] == "verified"

    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    c.issue(sig)

    # verified state must remain intact after halt + drain
    assert c.persistence().get_verified("goal-1") == {"status": "verified", "hash": "abc"}
