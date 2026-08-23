from aios.verification.security import (
    SecurityReport,
    SecurityScan,
    SecurityVerifier,
)
from aios.verification._common import VerificationError


def test_scan_construction():
    s = SecurityScan("S1", findings=(("F1", "low"),))
    assert s.scan_id == "S1"


def test_verify_pass_without_blocking():
    v = SecurityVerifier()
    s = SecurityScan("S1", findings=(("F1", "low"), ("F2", "medium")))
    rep = v.verify(s)
    assert isinstance(rep, SecurityReport)
    assert rep.blocking_findings == ()
    assert rep.status == "PASS"


def test_verify_insufficient_with_blocking():
    v = SecurityVerifier()
    s = SecurityScan("S1", findings=(("F1", "critical"), ("F2", "low")))
    rep = v.verify(s)
    assert len(rep.blocking_findings) == 1
    assert rep.status == "INSUFFICIENT"


def test_verify_rejects_empty_scan_id():
    v = SecurityVerifier()
    try:
        v.verify(SecurityScan(""))
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_rejects_non_scan():
    v = SecurityVerifier()
    try:
        v.verify("not-a-scan")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_case_insensitive_severity():
    v = SecurityVerifier()
    s = SecurityScan("S1", findings=(("F1", "CRITICAL"),))
    rep = v.verify(s)
    assert rep.status == "INSUFFICIENT"


def test_verify_deterministic_report_id():
    v = SecurityVerifier()
    s = SecurityScan("S1", findings=(("F1", "low"),))
    assert v.verify(s).report_id == v.verify(s).report_id
