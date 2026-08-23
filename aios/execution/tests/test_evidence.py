"""Tests for execution evidence + conformance (T144)."""

import pytest

from aios.execution import EvidenceStatus, ExecutionEvidence, ExecutionEvidenceRegistry
from aios.execution._common import ExecutionError, _hash


def _evidence(ev_id="ev1", verified=False):
    return ExecutionEvidence(
        evidence_id=ev_id,
        pipeline_ref="T135->T143",
        content_hash=_hash("payload"),
        producer="test-runner",
        evidence_chain=["ev-a", "ev-b"],
        integrity_verified=verified,
        policy_ref="pol1",
    )


def test_record_immutable_id():
    reg = ExecutionEvidenceRegistry()
    reg.record(_evidence("ev1"))
    with pytest.raises(ExecutionError):
        reg.record(_evidence("ev1"))


def test_promote_requires_verified():
    reg = ExecutionEvidenceRegistry()
    reg.record(_evidence("ev1", verified=False))
    with pytest.raises(ExecutionError):
        reg.get("ev1").promote()


def test_promote_when_verified():
    reg = ExecutionEvidenceRegistry()
    reg.record(_evidence("ev1", verified=True))
    reg.get("ev1").promote()
    assert reg.get("ev1").status == EvidenceStatus.VERIFIED


def test_conformance_verdict():
    reg = ExecutionEvidenceRegistry()
    reg.record(_evidence("ev1", verified=True))
    reg.get("ev1").promote()
    conf = reg.conformance("ev1")
    assert conf["verdict"] == "PASS"
    assert conf["evidence_chain"] == ["ev-a", "ev-b"]


def test_conformance_block_when_unverified():
    reg = ExecutionEvidenceRegistry()
    reg.record(_evidence("ev1", verified=False))
    conf = reg.conformance("ev1")
    assert conf["verdict"] == "BLOCK"


def test_content_hash_required():
    with pytest.raises(ExecutionError):
        ExecutionEvidence(evidence_id="ev1", pipeline_ref="x", content_hash="", producer="p")


def test_unknown_evidence():
    reg = ExecutionEvidenceRegistry()
    with pytest.raises(ExecutionError):
        reg.get("missing")
