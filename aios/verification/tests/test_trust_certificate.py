from aios.verification.trust_certificate import (
    CodingCertificate,
    TrustEvaluator,
    TrustReport,
    VerificationHarness,
)
from aios.verification._common import VerificationError


def test_certificate_construction():
    cert = CodingCertificate("C1", "module_x")
    assert cert.cert_id == "C1"
    assert cert.subject == "module_x"


def test_evaluate_high_trust_when_all_pass():
    ev = TrustEvaluator()
    cert = CodingCertificate("C1", "m")
    rep = ev.evaluate(cert, ["PASS", "PASS", "PASS", "PASS", "PASS"])
    assert isinstance(rep, TrustReport)
    assert rep.trust_level == "HIGH"
    assert rep.status == "PASS"


def test_evaluate_low_trust_when_mixed():
    ev = TrustEvaluator()
    cert = CodingCertificate("C1", "m")
    rep = ev.evaluate(cert, ["PASS", "INSUFFICIENT", "PASS"])
    assert rep.trust_level in ("MEDIUM", "LOW")
    assert rep.status == "INSUFFICIENT"


def test_evaluate_none_when_all_fail():
    ev = TrustEvaluator()
    cert = CodingCertificate("C1", "m")
    rep = ev.evaluate(cert, ["INSUFFICIENT", "INSUFFICIENT"])
    assert rep.trust_level == "NONE"
    assert rep.status == "INSUFFICIENT"


def test_harness_run_end_to_end():
    h = VerificationHarness()
    cert, rep = h.run("module_x", [("behavioral", "PASS"), ("security", "PASS"), ("regression", "PASS")])
    assert isinstance(cert, CodingCertificate)
    assert rep.status == "PASS"
    assert rep.trust_level == "HIGH"


def test_harness_rejects_empty_verifier_name():
    h = VerificationHarness()
    try:
        h.run("m", [("", "PASS")])
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_harness_rejects_empty_subject():
    h = VerificationHarness()
    try:
        h.run("", [("behavioral", "PASS")])
        assert False, "expected VerificationError"
    except VerificationError:
        pass
