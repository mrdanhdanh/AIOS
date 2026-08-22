"""Tests for TASK-098 — Remediation Integrity + Kill Switch (M14)."""

from __future__ import annotations

from aios.kill_switch.controller import KillSwitchController
from aios.remediation_integrity.integrity import (
    RemediationArtifact,
    RemediationIntegrity,
    RemediationIntegrityGate,
)
from aios.verification_integrity.integrity import sha256


def _artifact(artifact_id: str = "a1", content: str = "safe-config") -> RemediationArtifact:
    return RemediationArtifact(artifact_id, content, expected_hash=sha256(content))


def _gate() -> RemediationIntegrityGate:
    return RemediationIntegrityGate()


def test_integrity_pass_matching_hashes():
    eng = _gate()
    arts = [_artifact("a1", "cfg"), _artifact("a2", "plan")]
    res = eng.check("rem-1", arts, audit_trail=["step1", "step2"])
    assert isinstance(res, RemediationIntegrity)
    assert res.tampered is False
    assert res.passed is True


def test_tampered_artifact_rejected():
    eng = _gate()
    good = _artifact("a1", "cfg")
    bad = RemediationArtifact("a2", "plan", expected_hash=sha256("OTHER"))  # mismatch
    res = eng.check("rem-1", [good, bad], audit_trail=["step1"])
    assert res.tampered is True
    assert res.passed is False  # fail-closed reject


def test_kill_switch_halts_remediation():
    eng = RemediationIntegrityGate(kill_switch=KillSwitchController())
    eng.hook_kill_switch("rem-1")
    assert eng.should_halt("rem-1") is False  # not halted yet
    eng.issue_halt("dangerous drift detected", evidence_ref="ev-halt")
    assert eng.should_halt("rem-1") is True  # respects T068 halt


def test_missing_audit_trail_rejected():
    eng = _gate()
    arts = [_artifact("a1", "cfg")]
    res = eng.check("rem-1", arts, audit_trail=[])  # no audit trail
    assert res.passed is False  # fail-closed: audit required


def test_deterministic_integrity():
    eng = _gate()
    arts = [_artifact("a1", "cfg"), _artifact("a2", "plan")]
    r1 = eng.check("rem-1", arts, audit_trail=["s1", "s2"])
    r2 = eng.check("rem-1", arts, audit_trail=["s1", "s2"])
    assert eng.result_hash(r1) == eng.result_hash(r2)
    assert r1.passed == r2.passed
    assert r1.tampered == r2.tampered


def test_provenance_complete():
    eng = _gate()
    arts = [_artifact("a1", "cfg")]
    res = eng.check("rem-1", arts, audit_trail=["step1"])
    assert eng.provenance_complete(res) is True
    assert res.evidence_ref
