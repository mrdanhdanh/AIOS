from aios.quality_gate.risk_model import RiskAsset, RiskModel, RiskReport
from aios.quality_gate._common import QualityGateError


def test_risk_asset_construction_immutable():
    a = RiskAsset("A1", "POSSIBLE", "MODERATE")
    assert a.asset_id == "A1"


def test_risk_low_classification():
    m = RiskModel()
    rep = m.classify(RiskAsset("A1", "RARE", "NEGLIGIBLE"))
    assert isinstance(rep, RiskReport)
    assert rep.level == "LOW"


def test_risk_critical_classification():
    m = RiskModel()
    rep = m.classify(RiskAsset("A1", "CERTAIN", "SEVERE"))
    assert rep.level == "CRITICAL"
    assert rep.score == 25


def test_risk_medium_classification():
    m = RiskModel()
    rep = m.classify(RiskAsset("A1", "POSSIBLE", "MODERATE"))
    assert rep.level == "MEDIUM"


def test_risk_rejects_invalid_likelihood():
    m = RiskModel()
    try:
        m.classify(RiskAsset("A1", "NOPE", "MODERATE"))
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_risk_rejects_non_asset():
    m = RiskModel()
    try:
        m.classify("not-an-asset")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_risk_deterministic_report_id():
    m = RiskModel()
    a = m.classify(RiskAsset("A1", "LIKELY", "MAJOR"))
    b = m.classify(RiskAsset("A1", "LIKELY", "MAJOR"))
    assert a.report_id == b.report_id
