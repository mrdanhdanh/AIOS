"""Automated tests for the runtime audit trail (TASK-004)."""

import pytest

from aios.runtime.audit import AuditStatus, AuditTrail


def test_record_returns_sealed_event():
    trail = AuditTrail()
    ev = trail.record("agent-1", "tool.invoke", "tool:calc")
    assert ev.hash is not None
    assert ev.prev_hash is None
    assert len(trail) == 1


def test_chain_links_prev_hash():
    trail = AuditTrail()
    e1 = trail.record("a", "x", "r1")
    e2 = trail.record("a", "y", "r2")
    assert e2.prev_hash == e1.hash
    assert trail.verify_integrity()


def test_integrity_breaks_on_tamper():
    trail = AuditTrail()
    trail.record("a", "x", "r1")
    trail.record("a", "y", "r2")
    # Tamper with the first event's metadata.
    trail._events[0].metadata["hacked"] = True
    assert not trail.verify_integrity()


def test_integrity_breaks_on_reorder():
    trail = AuditTrail()
    trail.record("a", "x", "r1")
    trail.record("a", "y", "r2")
    trail.record("a", "z", "r3", context_id="r3")
    # Swap two events to break the chain linkage.
    trail._events[0], trail._events[1] = trail._events[1], trail._events[0]
    assert not trail.verify_integrity()


def test_query_by_actor():
    trail = AuditTrail()
    trail.record("alice", "read", "res-1")
    trail.record("bob", "read", "res-2")
    alice_events = trail.query(actor="alice")
    assert len(alice_events) == 1
    assert alice_events[0].actor == "alice"


def test_query_by_context_and_status():
    trail = AuditTrail()
    trail.record("a", "exec", "w1", context_id="c1", status=AuditStatus.OK)
    trail.record("a", "exec", "w2", context_id="c1", status=AuditStatus.DENIED)
    denied = trail.query(context_id="c1", status=AuditStatus.DENIED)
    assert len(denied) == 1
    assert denied[0].status == AuditStatus.DENIED


def test_root_hash_available():
    trail = AuditTrail()
    trail.record("a", "x", "r1")
    trail.record("a", "y", "r2")
    assert trail.root_hash == trail._events[-1].hash


def test_record_metadata_preserved():
    trail = AuditTrail()
    ev = trail.record("a", "invoke", "cap:math", metadata={"k": "v", "n": 3})
    assert ev.metadata == {"k": "v", "n": 3}
