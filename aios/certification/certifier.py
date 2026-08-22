"""Certifier."""
from __future__ import annotations

import time

from aios.certification.contracts import (
    CertProfile,
    CertStatus,
    Certification,
    RevocationReason,
)
from aios.certification.pipeline import CertPipeline


class Certifier:
    def __init__(self, ttl_seconds: float = 86400.0) -> None:
        self._certs: dict[str, Certification] = {}
        self._profiles: dict[str, CertProfile] = {}
        self._pipeline = CertPipeline()
        self._ttl = ttl_seconds

    def register_check(self, name: str, fn) -> None:
        self._pipeline.register_check(name, fn)

    def register_profile(self, profile: CertProfile) -> CertProfile:
        self._profiles[profile.profile_id] = profile
        return profile

    def issue(self, target_id: str, issuer: str = "system") -> Certification:
        cert = Certification(target_id=target_id, issuer=issuer)
        self._certs[cert.cert_id] = cert
        return cert

    def certify(self, cert_id: str, profile_id: str = "") -> Certification:
        """Certify only after the profile's checks pass (fail-closed)."""
        c = self._certs.get(cert_id)
        if c is None: raise RuntimeError(f"Cert {cert_id!r} not found")
        profile = self._profiles.get(profile_id)
        if profile is not None:
            c.profile_id = profile.profile_id
            all_passed, checks, signature = self._pipeline.run(c.target_id, profile.checks)
            c.evidence = [f"{chk.name}:{'pass' if chk.passed else 'fail'}" for chk in checks]
            c.signature = signature
            if not all_passed:
                c.status = CertStatus.PENDING
                return c
        c.status = CertStatus.CERTIFIED
        c.issued_at = time.time()
        c.expires_at = c.issued_at + self._ttl
        return c

    def revalidate(self, cert_id: str) -> Certification:
        """Re-run the certification (resets issued/expiry if still valid)."""
        c = self._certs.get(cert_id)
        if c is None: raise RuntimeError(f"Cert {cert_id!r} not found")
        if c.profile_id:
            return self.certify(cert_id, c.profile_id)
        c.issued_at = time.time()
        c.expires_at = c.issued_at + self._ttl
        c.status = CertStatus.CERTIFIED
        return c

    def revoke(self, cert_id: str, reason: RevocationReason = RevocationReason.MANUAL) -> Certification:
        c = self._certs.get(cert_id)
        if c is None: raise RuntimeError(f"Cert {cert_id!r} not found")
        c.status = CertStatus.REVOKED
        c.revocation_reason = reason.value
        return c

    def is_certified(self, target_id: str) -> bool:
        now = time.time()
        return any(
            c.target_id == target_id
            and c.status == CertStatus.CERTIFIED
            and (c.expires_at == 0.0 or c.expires_at > now)
            for c in self._certs.values()
        )

    def list_certs(self) -> list[Certification]: return list(self._certs.values())
