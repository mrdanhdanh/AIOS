from aios.evaluation.regression_detector import (
    RegressionCheck,
    RegressionDetector,
    RegressionReport,
)
from aios.evaluation._common import EvaluationError


def test_regression_construction_immutable():
    c = RegressionCheck("subj", 0.9, 0.8)
    assert c.subject == "subj"


def test_regression_pass_when_improved():
    d = RegressionDetector()
    rep = d.detect(RegressionCheck("subj", 0.9, 0.8, higher_is_better=True))
    assert isinstance(rep, RegressionReport)
    assert rep.status == "PASS"
    assert abs(rep.delta - 0.1) < 1e-9


def test_regression_insufficient_when_regressed():
    d = RegressionDetector()
    rep = d.detect(RegressionCheck("subj", 0.7, 0.8, higher_is_better=True))
    assert rep.status == "INSUFFICIENT"


def test_regression_unknown_when_no_baseline():
    d = RegressionDetector()
    rep = d.detect(RegressionCheck("subj", 0.9, None))
    assert rep.status == "UNKNOWN"
    assert rep.delta is None


def test_regression_lower_is_better_inverts():
    d = RegressionDetector()
    rep = d.detect(RegressionCheck("subj", 0.9, 0.8, higher_is_better=False))
    assert rep.status == "INSUFFICIENT"


def test_regression_rejects_non_check():
    d = RegressionDetector()
    try:
        d.detect("not-a-check")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_regression_deterministic_report_id():
    d = RegressionDetector()
    a = d.detect(RegressionCheck("subj", 0.9, 0.8))
    b = d.detect(RegressionCheck("subj", 0.9, 0.8))
    assert a.report_id == b.report_id
