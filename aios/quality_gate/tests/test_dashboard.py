from aios.quality_gate.dashboard import (
    DashboardReport,
    GovernanceHarness,
    GovernanceHarnessReport,
    QualityDashboard,
)
from aios.quality_gate._common import QualityGateError


def test_dashboard_construction():
    d = QualityDashboard()
    assert isinstance(d, QualityDashboard)


def test_dashboard_aggregate_ok():
    d = QualityDashboard()
    rep = d.aggregate([1, 2, 3])
    assert isinstance(rep, DashboardReport)
    assert rep.components == 3
    assert rep.summary == "OK"


def test_dashboard_aggregate_empty():
    d = QualityDashboard()
    rep = d.aggregate([])
    assert rep.summary == "EMPTY"


def test_dashboard_rejects_none_reports():
    d = QualityDashboard()
    try:
        d.aggregate(None)
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_harness_run_integrates_components():
    h = GovernanceHarness()
    rep = h.run("subject-x")
    assert isinstance(rep, GovernanceHarnessReport)
    assert rep.gate
    assert rep.risk
    assert rep.policy
    assert rep.release


def test_harness_rejects_empty_subject():
    h = GovernanceHarness()
    try:
        h.run("")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_harness_deterministic_report_id():
    h = GovernanceHarness()
    a = h.run("subject-x")
    b = h.run("subject-x")
    assert a.report_id == b.report_id
