"""TASK-163 — Evidence Collector + Evidence Integrity (M22).

Deterministic evidence collection with content hashing and integrity
verification. Fail-closed: collected evidence must carry a content hash;
integrity check recomputes and compares (tamper -> INSUFFICIENT).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aios.verification._common import VerificationError, _hash, _now, redact_secret


@dataclass(frozen=True)
class CollectedEvidence:
    evidence_id: str
    source: str
    content: str
    content_hash: str

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise VerificationError("evidence_id must be non-empty")
        if not self.source:
            raise VerificationError("source must be non-empty")
        if not self.content_hash:
            raise VerificationError("content_hash must be non-empty (provenance)")


@dataclass(frozen=True)
class IntegrityReport:
    report_id: str
    evidence_ref: str
    integrity_ok: bool
    status: str  # PASS | INSUFFICIENT


class EvidenceCollector:
    """Collect evidence with a content hash and verify its integrity."""

    def collect(self, source: str, content: str, *, evidence_id: Optional[str] = None) -> CollectedEvidence:
        if not source:
            raise VerificationError("source must be non-empty")
        if content is None:
            raise VerificationError("content must be provided")
        safe = redact_secret(content)
        eid = evidence_id or _hash(f"{source}|{safe}")
        return CollectedEvidence(
            evidence_id=eid,
            source=source,
            content=safe,
            content_hash=_hash(safe),
        )

    def verify_integrity(self, evidence: CollectedEvidence) -> IntegrityReport:
        if not isinstance(evidence, CollectedEvidence):
            raise VerificationError("evidence must be a CollectedEvidence")
        if not evidence.evidence_id:
            raise VerificationError("evidence_id must be non-empty (provenance)")

        recomputed = _hash(evidence.content)
        ok = recomputed == evidence.content_hash
        status = "PASS" if ok else "INSUFFICIENT"
        report_id = _hash(f"{evidence.evidence_id}|{ok}")
        return IntegrityReport(
            report_id=report_id,
            evidence_ref=evidence.evidence_id,
            integrity_ok=ok,
            status=status,
        )
