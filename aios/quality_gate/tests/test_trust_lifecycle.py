from aios.quality_gate.trust_lifecycle import (
    TrustCertificate,
    TrustLifecycle,
    TrustReport,
)
from aios.quality_gate._common import QualityGateError


def test_trust_cert_construction_immutable():
    c = TrustCertificate("C1", "scope")
    assert c.cert_id == "C1"


def test_trust_invalidate():
    lc = TrustLifecycle()
    c = TrustCertificate("C1", "scope")
    inv = lc.invalidate(c, reason="breach")
    assert inv.state == "INVALID"


def test_trust_invalidate_rejects_empty_reason():
    lc = TrustLifecycle()
    c = TrustCertificate("C1", "scope")
    try:
        lc.invalidate(c, reason="")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_trust_selective_reverify():
    lc = TrustLifecycle()
    c = TrustCertificate("C1", "scope")
    rep = lc.reverify(c, ["a", "b", "a"])
    assert isinstance(rep, TrustReport)
    assert rep.reverified_scopes == ("a", "b")
    assert rep.state == "VALID"


def test_trust_reverify_rejects_none_scopes():
    lc = TrustLifecycle()
    c = TrustCertificate("C1", "scope")
    try:
        lc.reverify(c, None)
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_trust_rejects_invalid_state():
    try:
        TrustCertificate("C1", "scope", state="NOPE")
        assert False, "expected QualityGateError"
    except QualityGateError:
        pass


def test_trust_deterministic_report_id():
    lc = TrustLifecycle()
    c = TrustCertificate("C1", "scope")
    a = lc.reverify(c, ["a", "b"])
    b = lc.reverify(c, ["a", "b"])
    assert a.report_id == b.report_id
