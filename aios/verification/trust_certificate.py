"""TASK-164 — Trust Evaluator + CodingCertificate + Verification Harness (M22).

Integration harness that aggregates verifier results into a CodingCertificate
and a TrustReport. Deterministic, fail-closed: any verifier result that is not
PASS (INSUFFICIENT/UNKNOWN) lowers trust; UNKNOWN is never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class CodingCertificate:
    cert_id: str
    subject: str
    verifier_refs: tuple = field(default_factory=tuple)
    trust_score: float = 0.0
    status: str = "UNKNOWN"  # PASS | INSUFFICIENT | UNKNOWN

    def __post_init__(self) -> None:
        if not self.cert_id:
            raise VerificationError("cert_id must be non-empty")
        if not self.subject:
            raise VerificationError("subject must be non-empty")


@dataclass(frozen=True)
class TrustReport:
    report_id: str
    cert_ref: str
    trust_level: str  # HIGH | MEDIUM | LOW | NONE
    status: str  # PASS | INSUFFICIENT


TRUST_THRESHOLD = 0.8


class TrustEvaluator:
    """Evaluate trust from a set of verifier result statuses."""

    def evaluate(self, cert: CodingCertificate, result_statuses: List[str]) -> TrustReport:
        if not isinstance(cert, CodingCertificate):
            raise VerificationError("cert must be a CodingCertificate")
        if not cert.cert_id:
            raise VerificationError("cert_id must be non-empty (provenance)")

        total = len(result_statuses)
        if total == 0:
            trust_score = 0.0
        else:
            passed = sum(1 for s in result_statuses if s == "PASS")
            trust_score = passed / total

        if trust_score >= TRUST_THRESHOLD:
            trust_level = "HIGH"
            status = "PASS"
        elif trust_score >= 0.5:
            trust_level = "MEDIUM"
            status = "INSUFFICIENT"
        elif trust_score > 0.0:
            trust_level = "LOW"
            status = "INSUFFICIENT"
        else:
            trust_level = "NONE"
            status = "INSUFFICIENT"

        report_id = _hash(f"{cert.cert_id}|{trust_score:.4f}")
        return TrustReport(
            report_id=report_id,
            cert_ref=cert.cert_id,
            trust_level=trust_level,
            status=status,
        )


class VerificationHarness:
    """Drive the M22 verifier pipeline end-to-end (fail-closed).

    Accepts a list of (verifier_name, status) pairs and produces a certificate
    + trust report. Any break in provenance (empty verifier name) is rejected.
    """

    def __init__(self) -> None:
        self._evaluator = TrustEvaluator()

    def run(self, subject: str, results: List[Tuple[str, str]], *, cert_id: str = "") -> Tuple[CodingCertificate, TrustReport]:
        if not subject:
            raise VerificationError("subject must be non-empty")
        if not results:
            raise VerificationError("results must be provided")

        statuses: List[str] = []
        for name, status in results:
            if not name:
                raise VerificationError("verifier name must be non-empty (provenance)")
            if status not in ("PASS", "INSUFFICIENT", "UNKNOWN"):
                raise VerificationError(f"invalid status: {status}")
            statuses.append(status)

        cid = cert_id or _hash(f"{subject}|{len(results)}")
        cert = CodingCertificate(
            cert_id=cid,
            subject=subject,
            verifier_refs=tuple(name for name, _ in results),
            trust_score=0.0,
        )
        report = self._evaluator.evaluate(cert, statuses)
        cert = CodingCertificate(
            cert_id=cid,
            subject=subject,
            verifier_refs=tuple(name for name, _ in results),
            trust_score=report.trust_level == "HIGH" and TRUST_THRESHOLD or 0.0,
            status=report.status,
        )
        return cert, report
