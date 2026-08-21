"""Certifier."""
from __future__ import annotations
from aios.certification.contracts import Certification, CertStatus

class Certifier:
    def __init__(self) -> None:
        self._certs: dict[str, Certification] = {}
    def issue(self, target_id: str, issuer: str = "system") -> Certification:
        cert = Certification(target_id=target_id, issuer=issuer)
        self._certs[cert.cert_id] = cert
        return cert
    def certify(self, cert_id: str) -> Certification:
        c = self._certs.get(cert_id)
        if c is None: raise RuntimeError(f"Cert {cert_id!r} not found")
        c.status = CertStatus.CERTIFIED; return c
    def revoke(self, cert_id: str) -> Certification:
        c = self._certs.get(cert_id)
        if c is None: raise RuntimeError(f"Cert {cert_id!r} not found")
        c.status = CertStatus.REVOKED; return c
    def is_certified(self, target_id: str) -> bool:
        return any(c.target_id == target_id and c.status == CertStatus.CERTIFIED for c in self._certs.values())
    def list_certs(self) -> list[Certification]: return list(self._certs.values())
