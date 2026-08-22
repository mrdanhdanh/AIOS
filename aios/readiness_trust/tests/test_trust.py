"""Tests for TASK-092 — System Readiness vs Harness Trust (Test Matrix)."""

from __future__ import annotations

from aios.certification.contracts import CertStatus
from aios.harness_coverage.coverage import CoverageReport, Readiness
from aios.meta_harness.meta import MetaResult, MetaVerdict
from aios.readiness_trust.trust import CombinedTrust, ReadinessTrust, TrustGate


def _ready_coverage() -> CoverageReport:
    return CoverageReport(5, 5, 1.0, [], Readiness.READY, evidence_ref="ev-cov")


def _not_ready_coverage() -> CoverageReport:
    return CoverageReport(5, 2, 0.4, ["x"], Readiness.NOT_READY, evidence_ref="ev-cov2")


def _meta_pass() -> MetaResult:
    return MetaResult(checks=[], verdict=MetaVerdict.PASS, evidence_ref="ev-meta")


def _meta_fail() -> MetaResult:
    return MetaResult(checks=[], verdict=MetaVerdict.FAIL, evidence_ref="ev-meta2")


def test_ready_and_trusted_certifies():
    gate = TrustGate()
    trust = gate.evaluate(True, _ready_coverage(), _meta_pass(), evidence_ref="ev-1")
    assert trust.combined is CombinedTrust.READY_TRUSTED
    cert = gate.certify(trust, target_id="build-1")
    assert cert is not None
    assert cert.status is CertStatus.CERTIFIED


def test_ready_but_untrusted_not_certified_fail_closed():
    gate = TrustGate()
    # system ready but harness untrusted (meta FAIL)
    trust = gate.evaluate(True, _ready_coverage(), _meta_fail(), evidence_ref="ev-2")
    assert trust.combined is CombinedTrust.READY_UNTRUSTED
    assert trust.harness_trusted is False
    assert gate.certify(trust, target_id="build-2") is None


def test_not_ready_but_trusted_not_certified():
    gate = TrustGate()
    trust = gate.evaluate(False, _ready_coverage(), _meta_pass(), evidence_ref="ev-3")
    assert trust.combined is CombinedTrust.NOT_READY
    assert gate.certify(trust, target_id="build-3") is None


def test_trust_decision_evidence_provenance():
    gate = TrustGate()
    trust = gate.evaluate(True, _ready_coverage(), _meta_pass(), evidence_ref="ev-4")
    assert gate.provenance_complete(trust) is True


def test_same_system_same_trust_deterministic():
    gate = TrustGate()
    t1 = gate.evaluate(True, _ready_coverage(), _meta_pass(), evidence_ref="ev-5")
    t2 = gate.evaluate(True, _ready_coverage(), _meta_pass(), evidence_ref="ev-5")
    assert gate.trust_hash(t1) == gate.trust_hash(t2)
    assert t1.combined == t2.combined


def test_combined_gate_logic():
    gate = TrustGate()
    # not ready + trusted -> NOT_READY
    assert (
        gate.evaluate(False, _ready_coverage(), _meta_pass()).combined
        is CombinedTrust.NOT_READY
    )
    # ready + untrusted (coverage not ready) -> READY_UNTRUSTED
    assert (
        gate.evaluate(True, _not_ready_coverage(), _meta_pass()).combined
        is CombinedTrust.READY_UNTRUSTED
    )
    # ready + trusted -> READY_TRUSTED
    assert (
        gate.evaluate(True, _ready_coverage(), _meta_pass()).combined
        is CombinedTrust.READY_TRUSTED
    )
