from aios.verification.regression import (
    RegressionCheck,
    RegressionReport,
    RegressionVerifier,
)
from aios.verification._common import VerificationError


def test_check_construction():
    c = RegressionCheck("R1", "latency", baseline=100.0, current=90.0)
    assert c.metric == "latency"


def test_verify_pass_when_improved():
    v = RegressionVerifier()
    c = RegressionCheck("R1", "latency", baseline=100.0, current=110.0, higher_is_better=True)
    rep = v.verify(c)
    assert isinstance(rep, RegressionReport)
    assert rep.regressed is False
    assert rep.status == "PASS"


def test_verify_insufficient_on_regression():
    v = RegressionVerifier()
    c = RegressionCheck("R1", "latency", baseline=100.0, current=80.0, higher_is_better=True)
    rep = v.verify(c)
    assert rep.regressed is True
    assert rep.status == "INSUFFICIENT"


def test_verify_lower_is_better_direction():
    v = RegressionVerifier()
    c = RegressionCheck("R1", "errors", baseline=5.0, current=2.0, higher_is_better=False)
    rep = v.verify(c)
    assert rep.regressed is False
    assert rep.status == "PASS"


def test_verify_rejects_empty_check_id():
    v = RegressionVerifier()
    try:
        v.verify(RegressionCheck("", "m", baseline=1.0, current=1.0))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_rejects_non_check():
    v = RegressionVerifier()
    try:
        v.verify("not-a-check")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_deterministic_report_id():
    v = RegressionVerifier()
    c = RegressionCheck("R1", "m", baseline=1.0, current=1.0)
    assert v.verify(c).report_id == v.verify(c).report_id
