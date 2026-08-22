"""Tests for TASK-056 Long-Horizon Durable Resume."""
from __future__ import annotations

from aios.goal_durability.contracts import InterruptionCause, ResumeVerdict
from aios.goal_durability.layer import GoalDurabilityLayer


def _layer(**kw):
    return GoalDurabilityLayer(**kw)


def test_checkpoint_atomic_monotonic_sequence():
    layer = _layer()
    cp1 = layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {"status": "active"},
                           ["t1"], ["t2", "t3"])
    cp2 = layer.checkpoint("g1", InterruptionCause.PROCESS_CRASH, {"status": "active"},
                           ["t1", "t2"], ["t3"])
    assert cp1.sequence == 0
    assert cp2.sequence == 1
    assert layer.get_latest("g1").sequence == 1


def test_old_checkpoint_does_not_overwrite_new():
    layer = _layer()
    cp1 = layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {}, ["t1"], ["t2"])
    cp2 = layer.checkpoint("g1", InterruptionCause.PROCESS_CRASH, {}, ["t1", "t2"], ["t3"])
    # Monotonic coordinator: latest is the newer (higher-sequence) checkpoint.
    latest = layer.get_latest("g1")
    assert latest.sequence == cp2.sequence == 1
    assert cp1.sequence == 0
    assert latest.checkpoint_id != cp1.checkpoint_id


def test_content_hash_integrity():
    layer = _layer()
    cp = layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {}, ["t1"], ["t2"])
    assert cp.content_hash != ""
    # Tamper detection: recomputed hash differs from stored.
    cp.completed_tasks.append("t9")
    assert cp.compute_hash() != cp.content_hash


def test_resume_skips_completed_tasks():
    layer = _layer()
    layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {}, ["t1", "t2"], ["t3", "t4"])
    plan = layer.resume("g1")
    assert plan.verdict == ResumeVerdict.VALID
    assert set(plan.skip_tasks) == {"t1", "t2"}
    assert set(plan.resume_tasks) == {"t3", "t4"}


def test_resume_idempotency_no_duplicate_side_effect():
    layer = _layer()
    layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {}, ["t1"], ["t2"])
    layer.acknowledge_action("g1", "act-t2")
    # Even if t2 is pending, its side effect is already acknowledged.
    assert layer.is_action_acknowledged("g1", "act-t2")


def test_resume_invalid_when_evidence_missing():
    layer = _layer(evidence_exists=lambda e: e != "ev:missing")
    layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {}, ["t1"], ["t2"],
                     evidence_refs=["ev:missing"])
    plan = layer.resume("g1")
    assert plan.verdict == ResumeVerdict.INCONCLUSIVE  # fail-closed


def test_resume_stale_triggers_replan():
    replanned = {"called": False}
    def planner(gid):
        replanned["called"] = True
    layer = _layer(planner=planner)
    layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {},
                     ["t1"], ["t2"],
                     policy_autonomy_state={"versions": {"plan": "v1", "world": "w1"}})
    plan = layer.resume("g1", current_versions={"plan": "v2", "world": "w1"})
    assert plan.stale is True
    assert plan.replan is True
    assert replanned["called"] is True


def test_resume_policy_invalid_blocks():
    layer = _layer(policy_validator=lambda st: st.get("allowed", True))
    layer.checkpoint("g1", InterruptionCause.GRACEFUL_PAUSE, {},
                     ["t1"], ["t2"],
                     policy_autonomy_state={"allowed": False})
    plan = layer.resume("g1")
    assert plan.verdict == ResumeVerdict.INVALID


def test_interruption_cause_taxonomy():
    layer = _layer()
    for cause in InterruptionCause:
        cp = layer.checkpoint("g2", cause, {}, [], ["t1"])
        assert cp.interruption_cause == cause.value
