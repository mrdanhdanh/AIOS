"""Tests for the verification engine (T142)."""

import pytest

from aios.execution import (
    CollectedArtifact,
    OutputArtifactCollector,
    VerificationEngine,
    VerificationResult,
    VerifyStatus,
)
from aios.execution._common import ExecutionError


def _artifact():
    c = OutputArtifactCollector(policy_ref="pol1")
    out = c.capture_output("run1", "stdout", "hello world")
    return c.collect("run1", [out])


def test_verify_pass_promotes():
    e = VerificationEngine()
    res = e.verify(_artifact(), expected=VerifyStatus.PASS)
    assert res.verification_result == VerifyStatus.PASS
    assert res.integrity_verified is True


def test_verify_fail_not_promoted():
    e = VerificationEngine()
    res = e.verify(_artifact(), expected=VerifyStatus.FAIL)
    assert res.integrity_verified is False


def test_verify_inconclusive_not_promoted():
    e = VerificationEngine()
    res = e.verify(_artifact(), expected=VerifyStatus.INCONCLUSIVE)
    assert res.integrity_verified is False


def test_verify_no_hash_fails():
    e = VerificationEngine()
    art = CollectedArtifact(run_ref="run1")  # no outputs -> empty hash
    with pytest.raises(ExecutionError):
        e.verify(art)


def test_authority_must_be_aios():
    with pytest.raises(ExecutionError):
        VerificationResult(collected_ref="c1", verification_result=VerifyStatus.PASS, integrity_verified=True, authority="other")


def test_provenance():
    e = VerificationEngine()
    res = e.verify(_artifact(), expected=VerifyStatus.PASS)
    prov = e.provenance(res)
    assert prov["verification_result"] == "PASS"
    assert prov["content_hash"]
