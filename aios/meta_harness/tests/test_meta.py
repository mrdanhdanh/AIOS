"""Tests for TASK-091 — Meta-Harness / Verify-the-Verifier (Test Matrix)."""

from __future__ import annotations

from aios.harness_coverage.coverage import CoverageMap, CoverageReport, Readiness
from aios.meta_harness.meta import MetaCheck, MetaHarness, MetaVerdict


def _good_harness(subject) -> str:
    """A correct harness: returns 'pass' for clean input, 'fail' for bad input."""
    return "pass" if subject == "clean" else "fail"


def _bad_harness(subject) -> str:
    """A broken harness: always returns 'pass' (misses the bad case)."""
    return "pass"


def test_known_answer_correct_meta_pass():
    mh = MetaHarness()
    chk = mh.known_answer_check("h1", _good_harness, "clean", "pass", run_id="r1")
    assert chk.known_answer_correct is True
    assert chk.verifier_locked is True
    result = mh.evaluate([chk], evidence_ref="ev-1")
    assert result.verdict is MetaVerdict.PASS


def test_harness_wrong_verdict_meta_fail():
    mh = MetaHarness()
    chk = mh.known_answer_check("h1", _bad_harness, "dirty", "fail", run_id="r2")
    assert chk.known_answer_correct is False
    result = mh.evaluate([chk], evidence_ref="ev-2")
    assert result.verdict is MetaVerdict.FAIL  # fail-closed


def test_mutation_detected_meta_pass():
    mh = MetaHarness()
    chk = mh.mutation_check("h1", _good_harness, "clean", "dirty", run_id="r3")
    assert chk.mutation_detected is True
    result = mh.evaluate([chk], evidence_ref="ev-3")
    assert result.verdict is MetaVerdict.PASS


def test_mutation_undetected_meta_fail():
    mh = MetaHarness()
    # _bad_harness returns 'pass' for both -> mutation NOT detected.
    chk = mh.mutation_check("h1", _bad_harness, "clean", "dirty", run_id="r4")
    assert chk.mutation_detected is False
    result = mh.evaluate([chk], evidence_ref="ev-4")
    assert result.verdict is MetaVerdict.FAIL


def test_verifier_not_locked_blocked():
    # A MetaCheck with verifier_locked=False must force meta FAIL (T078).
    chk = MetaCheck(
        harness_under_test="h1",
        known_answer="pass",
        known_answer_correct=True,
        mutation_detected=True,
        verifier_locked=False,
        evidence_ref="ev-5",
    )
    mh = MetaHarness()
    result = mh.evaluate([chk], evidence_ref="ev-5")
    assert result.verdict is MetaVerdict.FAIL


def test_same_meta_input_same_result_deterministic():
    mh = MetaHarness()
    c1 = mh.known_answer_check("h1", _good_harness, "clean", "pass", run_id="r6")
    c2 = mh.known_answer_check("h1", _good_harness, "clean", "pass", run_id="r6")
    r1 = mh.evaluate([c1], evidence_ref="ev-6")
    r2 = mh.evaluate([c2], evidence_ref="ev-6")
    assert mh.result_hash(r1) == mh.result_hash(r2)


def test_require_readiness_gates_meta():
    mh = MetaHarness()
    ready = CoverageReport(5, 5, 1.0, [], Readiness.READY, evidence_ref="ev-7")
    not_ready = CoverageReport(5, 2, 0.4, ["x"], Readiness.NOT_READY, evidence_ref="ev-8")
    assert mh.require_readiness(ready) is True
    assert mh.require_readiness(not_ready) is False
