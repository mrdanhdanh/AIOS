"""Audit / evidence tests for Kill Switch (TASK-068)."""

from __future__ import annotations

from aios.governance.evidence.store import EvidenceStore

from aios.kill_switch.audit import AuditLog
from aios.kill_switch.controller import KillSwitchController
from aios.kill_switch.tests.conftest import FakeContext, make_signal
from aios.kill_switch.contracts import HaltScope, HaltSource


def test_record_halt_creates_admissible_evidence():
    audit = AuditLog()
    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    ref = audit.record_halt(sig, ["loop-1"], ["loop-1"])
    assert ref
    assert audit.provenance_complete(ref) is True


def test_record_halt_is_idempotent():
    audit = AuditLog()
    sig = make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop")
    r1 = audit.record_halt(sig, ["loop-1"], ["loop-1"])
    r2 = audit.record_halt(sig, ["loop-1", "loop-2"], ["loop-1"])
    assert r1 == r2
    # only one evidence record for the signal
    assert len([e for e in audit.store().list_all() if e.evidence_id == r1]) == 1


def test_controller_audit_uses_shared_evidence_store():
    store = EvidenceStore()
    c = KillSwitchController(evidence_store=store)
    c.register(FakeContext("loop-1", "loop"))
    res = c.issue(make_signal(HaltSource.MANUAL, HaltScope.GLOBAL, "stop"))
    # the shared store received the evidence
    assert store.get(res.evidence_ref).evidence_id == res.evidence_ref
    assert store.is_admissible(res.evidence_ref) is True
