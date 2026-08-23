"""TASK-194 — Evaluation Store (M25).

Stores evaluation records with content_hash integrity. Based on Evidence
Collector T163 + Integrity T078. Fail-closed: tamper -> INSUFFICIENT.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from aios.evaluation._common import EvaluationError, _hash, redact_secret


@dataclass(frozen=True)
class StoredEvaluation:
    record_id: str
    subject: str
    content: str
    content_hash: str

    def __post_init__(self) -> None:
        if not self.record_id:
            raise EvaluationError("record_id must be non-empty")
        if not self.subject:
            raise EvaluationError("subject must be non-empty")
        if not self.content_hash:
            raise EvaluationError("content_hash must be non-empty (provenance)")


@dataclass(frozen=True)
class StoreReport:
    report_id: str
    stored: int
    tampered: tuple


class EvaluationStore:
    """Store evaluation records with integrity verification."""

    def __init__(self) -> None:
        self._records: List[StoredEvaluation] = []

    def store(self, record: StoredEvaluation) -> StoreReport:
        if not isinstance(record, StoredEvaluation):
            raise EvaluationError("record must be a StoredEvaluation")
        # Fail-closed: recompute hash; mismatch -> reject.
        if _hash(redact_secret(record.content)) != record.content_hash:
            raise EvaluationError("content_hash mismatch (tamper detected)")
        self._records.append(record)
        report_id = _hash(f"{record.record_id}|{len(self._records)}")
        return StoreReport(report_id=report_id, stored=len(self._records), tampered=())

    def verify_integrity(self) -> StoreReport:
        tampered = tuple(
            r.record_id for r in self._records if _hash(redact_secret(r.content)) != r.content_hash
        )
        report_id = _hash(f"{len(self._records)}|{','.join(sorted(tampered))}")
        return StoreReport(report_id=report_id, stored=len(self._records), tampered=tampered)
