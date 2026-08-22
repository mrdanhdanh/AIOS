"""Tests for TASK-049 Certification (profiles, checks pipeline, expiry, revocation)."""

from __future__ import annotations

from aios.certification.certifier import Certifier
from aios.certification.contracts import CertCheck, CertProfile, CertStatus, RevocationReason


def test_profile_and_checks_pipeline() -> None:
    c = Certifier()
    c.register_check("has_manifest", lambda tid: CertCheck(name="has_manifest", passed=True))
    c.register_check("no_vulns", lambda tid: CertCheck(name="no_vulns", passed=True))
    prof = c.register_profile(CertProfile(name="ext", checks=["has_manifest", "no_vulns"]))
    cert = c.issue("target-1")
    c.certify(cert.cert_id, prof.profile_id)
    assert cert.status == CertStatus.CERTIFIED
    assert cert.signature != ""
    assert c.is_certified("target-1") is True


def test_fail_closed_on_failed_check() -> None:
    c = Certifier()
    c.register_check("bad", lambda tid: CertCheck(name="bad", passed=False))
    prof = c.register_profile(CertProfile(name="p", checks=["bad"]))
    cert = c.issue("t2")
    c.certify(cert.cert_id, prof.profile_id)
    assert cert.status == CertStatus.PENDING  # not certified


def test_revoke_with_reason() -> None:
    c = Certifier()
    cert = c.issue("t3")
    c.certify(cert.cert_id)
    c.revoke(cert.cert_id, RevocationReason.SECURITY)
    assert cert.status == CertStatus.REVOKED
    assert cert.revocation_reason == "security"
    assert c.is_certified("t3") is False


def test_revalidate_resets_expiry() -> None:
    c = Certifier(ttl_seconds=10.0)
    cert = c.issue("t4")
    c.certify(cert.cert_id)
    old = cert.expires_at
    c.revalidate(cert.cert_id)
    assert cert.expires_at >= old
