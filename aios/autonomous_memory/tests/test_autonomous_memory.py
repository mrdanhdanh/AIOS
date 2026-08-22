"""Tests for TASK-057 Autonomous Memory."""
from __future__ import annotations

from aios.autonomous_memory.contracts import (
    FailureMemoryEntry,
    GoalMemoryEntry,
    MemoryScope,
    TrustStatus,
    VerificationStatus,
)
from aios.autonomous_memory.controller import MemoryController
from aios.autonomous_memory.retention import RetentionPolicy


def _ctrl(**kw):
    return MemoryController(**kw)


def test_failure_memory_requires_valid_evidence():
    c = _ctrl(evidence_valid=lambda e: e == "ev:ok")
    bad = FailureMemoryEntry(goal_id="g1", failure_class="TRANSIENT", outcome="recovered", evidence_ref="")
    r = c.write_failure(bad)
    assert not r.persisted
    good = FailureMemoryEntry(goal_id="g1", failure_class="TRANSIENT", outcome="recovered", evidence_ref="ev:ok")
    r2 = c.write_failure(good)
    assert r2.persisted


def test_goal_memory_lesson_candidate_untrusted_on_write():
    c = _ctrl(evidence_valid=lambda e: True)
    e = GoalMemoryEntry(goal_id="g1", execution_id="x1", outcome="completed",
                        observation={"raw": "data"}, lesson_candidate="do X",
                        evidence_ref="ev:1")
    c.write_goal(e)
    assert e.verification_status == VerificationStatus.UNVERIFIED
    assert e.trust_status == TrustStatus.UNTRUSTED


def test_verify_promotes_to_trusted():
    c = _ctrl(evidence_valid=lambda e: True)
    e = GoalMemoryEntry(goal_id="g1", execution_id="x1", outcome="completed",
                        evidence_ref="ev:1")
    c.write_goal(e)
    assert c.verify_entry(e.entry_id)
    assert e.trust_status == TrustStatus.TRUSTED
    # Trusted-only read returns it.
    assert len(c.read(MemoryScope.GOAL.value, trusted_only=True)) == 1


def test_read_trusted_only_excludes_unverified():
    c = _ctrl(evidence_valid=lambda e: True)
    e = GoalMemoryEntry(goal_id="g1", execution_id="x1", outcome="completed", evidence_ref="ev:1")
    c.write_goal(e)
    assert len(c.read(MemoryScope.GOAL.value, trusted_only=True)) == 0
    assert len(c.read(MemoryScope.GOAL.value, trusted_only=False)) == 1


def test_governor_denial_blocks_persist():
    c = _ctrl(evidence_valid=lambda e: True, governor_allow=lambda a: False)
    e = FailureMemoryEntry(goal_id="g1", failure_class="RESOURCE", outcome="safe_stopped", evidence_ref="ev:1")
    r = c.write_failure(e)
    assert not r.persisted
    assert "governor" in r.reason


def test_deduplicate_failure_entries():
    c = _ctrl(evidence_valid=lambda e: True)
    e1 = FailureMemoryEntry(goal_id="g1", failure_class="TRANSIENT", outcome="recovered", evidence_ref="ev:1")
    e2 = FailureMemoryEntry(goal_id="g1", failure_class="TRANSIENT", outcome="recovered", evidence_ref="ev:2")
    c.write_failure(e1)
    c.write_failure(e2)
    assert len(c.read(MemoryScope.GOAL.value, trusted_only=False)) == 1


def test_retention_eviction_deterministic():
    pol = RetentionPolicy(max_size=1)
    c = MemoryController(evidence_valid=lambda e: True, retention=pol)
    e1 = GoalMemoryEntry(goal_id="g1", execution_id="x1", outcome="completed", evidence_ref="ev:1")
    e2 = GoalMemoryEntry(goal_id="g2", execution_id="x2", outcome="completed", evidence_ref="ev:2")
    c.write_goal(e1)
    c.write_goal(e2)
    # max_size=1 -> only 1 remains; lowest priority (unverified, older) evicted
    assert len(c.read(MemoryScope.GOAL.value, trusted_only=False)) == 1


def test_no_parallel_memory_store_created():
    # Controller wraps an injected store; it does not instantiate a vector/db.
    c = _ctrl(evidence_valid=lambda e: True)
    assert isinstance(c._store, dict)
