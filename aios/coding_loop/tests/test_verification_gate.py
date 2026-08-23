"""Tests for the verification gate (T151)."""

import pytest

from aios.coding_loop import ProgressRegressionDetector, VerifyStatus, VerificationGate
from aios.coding_loop._common import CodingLoopError


def _progress(regression, metric=0.8):
    d = ProgressRegressionDetector(baseline=0.5)
    return d.detect("loop1", "plan1", metric, evidence_ref="ev1") if not regression else d.detect(
        "loop1", "plan1", 0.2, evidence_ref="ev1"
    )


def test_verify_correct_output_pass():
    g = VerificationGate()
    prog = _progress(regression=False)
    res = g.verify(prog, output_hash="abc123", evidence_ref="ev1")
    assert res.verification_result == VerifyStatus.PASS
    assert g.is_promotable(res) is True


def test_verify_regression_fail():
    g = VerificationGate()
    prog = _progress(regression=True)
    res = g.verify(prog, output_hash="abc123", evidence_ref="ev1")
    assert res.verification_result == VerifyStatus.FAIL
    assert g.is_promotable(res) is False  # fail-closed (T078)


def test_verify_inconclusive_not_promoted():
    g = VerificationGate()
    prog = _progress(regression=False)
    res = g.verify(prog, output_hash="", evidence_ref="ev1")  # no hash -> INCONCLUSIVE
    assert res.verification_result == VerifyStatus.INCONCLUSIVE
    assert g.is_promotable(res) is False  # not promoted (T078)


def test_verify_requires_provenance():
    g = VerificationGate()
    prog = _progress(regression=False)
    from aios.coding_loop.progress_detection import ProgressReport

    bad = ProgressReport("p1", "loop1", "plan1", 0.8, False, evidence_ref="ev-tmp")
    object.__setattr__(bad, "evidence_ref", "")
    with pytest.raises(CodingLoopError):
        g.verify(bad, output_hash="abc")


def test_deterministic_same_output_same_result():
    g1 = VerificationGate()
    g2 = VerificationGate()
    p1 = _progress(regression=False)
    p2 = _progress(regression=False)
    assert g1.verify(p1, "abc", evidence_ref="ev1").verification_result == g2.verify(
        p2, "abc", evidence_ref="ev1"
    ).verification_result


def test_duplicate_result_id_rejected():
    g = VerificationGate()
    prog = _progress(regression=False)
    g.verify(prog, "abc", evidence_ref="ev1", result_id="ver1")
    with pytest.raises(CodingLoopError):
        g.verify(prog, "abc", evidence_ref="ev1", result_id="ver1")


def test_provenance_hash():
    g = VerificationGate()
    prog = _progress(regression=False)
    res = g.verify(prog, "abc", evidence_ref="ev1")
    prov = g.provenance(res.result_id)
    assert prov["content_hash"]
    assert prov["verification_result"] == "PASS"
