from aios.verification.evidence_collector import (
    CollectedEvidence,
    EvidenceCollector,
    IntegrityReport,
)
from aios.verification._common import VerificationError


def test_collect_construction_with_hash():
    c = EvidenceCollector()
    e = c.collect("src.py", "print(1)")
    assert isinstance(e, CollectedEvidence)
    assert e.content_hash
    assert e.evidence_id


def test_collect_redacts_secret():
    c = EvidenceCollector()
    e = c.collect("cfg", "api_key: secret123")
    assert "secret123" not in e.content
    assert "<REDACTED>" in e.content


def test_verify_integrity_pass():
    c = EvidenceCollector()
    e = c.collect("src.py", "print(1)")
    rep = c.verify_integrity(e)
    assert isinstance(rep, IntegrityReport)
    assert rep.integrity_ok is True
    assert rep.status == "PASS"


def test_verify_integrity_insufficient_on_tamper():
    c = EvidenceCollector()
    e = c.collect("src.py", "print(1)")
    bad = CollectedEvidence(e.evidence_id, e.source, "print(2)", e.content_hash)
    rep = c.verify_integrity(bad)
    assert rep.integrity_ok is False
    assert rep.status == "INSUFFICIENT"


def test_collect_rejects_empty_source():
    c = EvidenceCollector()
    try:
        c.collect("", "x")
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_verify_integrity_rejects_empty_evidence_id():
    c = EvidenceCollector()
    e = c.collect("src.py", "print(1)")
    bad = CollectedEvidence(e.evidence_id, e.source, e.content, e.content_hash)
    object.__setattr__(bad, "evidence_id", "")
    try:
        c.verify_integrity(bad)
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_collect_deterministic_evidence_id():
    c = EvidenceCollector()
    a = c.collect("src.py", "print(1)")
    b = c.collect("src.py", "print(1)")
    assert a.evidence_id == b.evidence_id
