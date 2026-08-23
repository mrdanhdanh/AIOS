"""Tests for progress + regression detection (T150)."""

import pytest

from aios.coding_loop import ProgressRegressionDetector
from aios.coding_loop._common import CodingLoopError


def test_progress_improving():
    d = ProgressRegressionDetector(baseline=0.5)
    rep = d.detect("loop1", "plan1", 0.8, evidence_ref="ev1")
    assert rep.progress_metric == 0.8
    assert rep.regression_flag is False


def test_regression_vs_baseline():
    d = ProgressRegressionDetector(baseline=0.5)
    rep = d.detect("loop1", "plan1", 0.2, evidence_ref="ev1")
    assert rep.regression_flag is True


def test_deterministic_same_state_same_verdict():
    d1 = ProgressRegressionDetector(baseline=0.5)
    d2 = ProgressRegressionDetector(baseline=0.5)
    a = d1.detect("loop1", "plan1", 0.2, evidence_ref="ev1")
    b = d2.detect("loop1", "plan1", 0.2, evidence_ref="ev1")
    assert a.regression_flag == b.regression_flag


def test_missing_evidence_rejected():
    d = ProgressRegressionDetector()
    with pytest.raises(CodingLoopError):
        d.detect("loop1", "plan1", 0.8, evidence_ref=None)  # fail-closed


def test_missing_loop_link_rejected():
    d = ProgressRegressionDetector()
    with pytest.raises(CodingLoopError):
        d.detect("", "plan1", 0.8, evidence_ref="ev1")


def test_duplicate_report_id_rejected():
    d = ProgressRegressionDetector()
    d.detect("loop1", "plan1", 0.8, evidence_ref="ev1", report_id="prog1")
    with pytest.raises(CodingLoopError):
        d.detect("loop1", "plan1", 0.8, evidence_ref="ev1", report_id="prog1")


def test_provenance_hash():
    d = ProgressRegressionDetector(baseline=0.5)
    rep = d.detect("loop1", "plan1", 0.2, evidence_ref="ev1")
    prov = d.provenance(rep.report_id)
    assert prov["content_hash"]
    assert prov["regression_flag"] is True
