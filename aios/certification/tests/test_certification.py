"""Tests for certification."""
from __future__ import annotations
import pytest
from aios.certification.contracts import Certification, CertStatus
from aios.certification.certifier import Certifier

class TestCertification:
    def test_issue(self):
        cert = Certifier()
        c = cert.issue("plugin-1")
        assert c.status == CertStatus.PENDING
    def test_certify_revoke(self):
        cert = Certifier()
        c = cert.issue("plugin-1")
        cert.certify(c.cert_id)
        assert c.status == CertStatus.CERTIFIED
        assert cert.is_certified("plugin-1")
        cert.revoke(c.cert_id)
        assert c.status == CertStatus.REVOKED
        assert not cert.is_certified("plugin-1")
    def test_not_found(self):
        cert = Certifier()
        with pytest.raises(RuntimeError): cert.certify("nonexistent")
    def test_list(self):
        cert = Certifier()
        cert.issue("a"); cert.issue("b")
        assert len(cert.list_certs()) == 2
    def test_to_dict(self):
        c = Certification(target_id="t1")
        d = c.to_dict()
        assert d["target_id"] == "t1"
