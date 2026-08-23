from aios.verification.performance import (
    PerfBudget,
    PerfReport,
    PerformanceVerifier,
)
from aios.verification._common import VerificationError


def test_budget_construction():
    b = PerfBudget("P1", "cpu", limit=100.0, observed=50.0)
    assert b.metric == "cpu"


def test_verify_pass_within_budget():
    v = PerformanceVerifier()
    b = PerfBudget("P1", "cpu", limit=100.0, observed=99.0)
    rep = v.verify(b)
    assert isinstance(rep, PerfReport)
    assert rep.within_budget is True
    assert rep.status == "PASS"


def test_verify_insufficient_over_budget():
    v = PerformanceVerifier()
    b = PerfBudget("P1", "cpu", limit=100.0, observed=150.0)
    rep = v.verify(b)
    assert rep.within_budget is False
    assert rep.status == "INSUFFICIENT"


def test_verify_rejects_empty_budget_id():
    v = PerformanceVerifier()
    try:
        v.verify(PerfBudget("", "cpu", limit=1.0, observed=1.0))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_rejects_non_budget():
    v = PerformanceVerifier()
    try:
        v.verify("not-a-budget")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_boundary_equal_is_pass():
    v = PerformanceVerifier()
    b = PerfBudget("P1", "cpu", limit=100.0, observed=100.0)
    rep = v.verify(b)
    assert rep.within_budget is True
    assert rep.status == "PASS"


def test_verify_deterministic_report_id():
    v = PerformanceVerifier()
    b = PerfBudget("P1", "cpu", limit=100.0, observed=50.0)
    assert v.verify(b).report_id == v.verify(b).report_id
