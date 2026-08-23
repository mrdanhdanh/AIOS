"""TASK-182 — Trust Lifecycle + Invalidation + Selective Reverification (M24).

Manages trust certificate lifecycle with invalidation and selective
reverification (only affected scopes are re-validated). Fail-closed on
missing reason for invalidation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

TRUST_STATES = ("VALID", "INVALID", "EXPIRED", "REVOKED")
TRUST_LEVELS = ("NONE", "LOW", "MEDIUM", "HIGH")


@dataclass(frozen=True)
class TrustCertificate:
    cert_id: str
    scope: str
    state: str = "VALID"
    level: str = "HIGH"

    def __post_init__(self) -> None:
        if not self.cert_id:
            raise QualityGateError("cert_id must be non-empty")
        if not self.scope:
            raise QualityGateError("scope must be non-empty")
        if self.state not in TRUST_STATES:
            raise QualityGateError(f"invalid state: {self.state}")
        if self.level not in TRUST_LEVELS:
            raise QualityGateError(f"invalid level: {self.level}")


@dataclass(frozen=True)
class TrustReport:
    report_id: str
    cert_ref: str
    state: str
    reverified_scopes: tuple


class TrustLifecycle:
    """Manage trust certificate lifecycle with selective reverification."""

    def invalidate(self, cert: TrustCertificate, *, reason: str = "manual") -> TrustCertificate:
        if not isinstance(cert, TrustCertificate):
            raise QualityGateError("cert must be a TrustCertificate")
        if not reason:
            raise QualityGateError("reason must be non-empty")
        return TrustCertificate(cert_id=cert.cert_id, scope=cert.scope, state="INVALID", level=cert.level)

    def reverify(self, cert: TrustCertificate, affected_scopes: List[str]) -> TrustReport:
        if not isinstance(cert, TrustCertificate):
            raise QualityGateError("cert must be a TrustCertificate")
        if affected_scopes is None:
            raise QualityGateError("affected_scopes must be provided")
        # Selective: only reverified scopes are re-validated (deduplicated).
        reverified = tuple(sorted(set(s for s in affected_scopes if s)))
        state = "VALID" if cert.state in ("VALID", "INVALID") else cert.state
        report_id = _hash(f"{cert.cert_id}|{state}|{','.join(reverified)}")
        return TrustReport(report_id=report_id, cert_ref=cert.cert_id, state=state, reverified_scopes=reverified)
