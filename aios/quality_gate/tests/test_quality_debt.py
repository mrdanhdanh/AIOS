from aios.quality_gate.quality_debt import DebtItem, DebtReport, QualityDebtTracker
from aios.quality_gate._common import QualityGateError


def test_debt_item_construction_immutable():
    d = DebtItem("D1", "LOW", 1)
    assert d.item_id == "D1"


def test_debt_healthy_when_no_critical():
    t = QualityDebtTracker()
    rep = t.track([DebtItem("D1", "LOW", 1), DebtItem("D2", "MEDIUM", 2)])
    assert isinstance(rep, DebtReport)
    assert rep.status == "HEALTHY"


def test_debt_at_risk_within_threshold():
    t = QualityDebtTracker()
    rep = t.track([DebtItem("D1", "HIGH", 1), DebtItem("D2", "MEDIUM", 2)])
    assert rep.status == "AT_RISK"


def test_debt_breach_over_threshold():
    t = QualityDebtTracker()
    rep = t.track([DebtItem("D1", "HIGH", 1), DebtItem("D2", "CRITICAL", 2), DebtItem("D3", "CRITICAL", 3), DebtItem("D4", "CRITICAL", 4)])
    assert rep.status == "BREACH"


def test_debt_rejects_invalid_severity():
    t = QualityDebtTracker()
    try:
        t.track([DebtItem("D1", "NOPE", 1)])
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_debt_rejects_negative_age():
    t = QualityDebtTracker()
    try:
        t.track([DebtItem("D1", "LOW", -1)])
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_debt_deterministic_report_id():
    t = QualityDebtTracker()
    a = t.track([DebtItem("D1", "HIGH", 1)])
    b = t.track([DebtItem("D1", "HIGH", 1)])
    assert a.report_id == b.report_id
