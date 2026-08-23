"""Context Verification + Evidence (TASK-123, M18).

Verifies a built context (T122) is correct/complete, runs the integrity gate
(T078), and records provenance (T001 Rule 5). Fail-closed: FAIL/INCONCLUSIVE
is never promoted to PASS. Deterministic. Secret isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aios.governance.evidence.store import EvidenceStore
from aios.verification_integrity.integrity import IntegrityChecker

from .common import ContextError, SecretBoundary, emit_evidence, sha256
from .builder import BuiltContext


__all__ = ["VerificationError", "VerificationVerdict", "VerificationResult", "ContextVerification"]


class VerificationError(ContextError):
    """Raised when verification cannot proceed (fail-closed, T078)."""


class VerificationVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class VerificationResult:
    built_context_ref: str
    verification_result: VerificationVerdict
    integrity_verified: bool
    evidence_ref: str
    authority: str = "aios"
    content_hash: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "built_context_ref": self.built_context_ref,
            "verification_result": self.verification_result.value,
            "integrity_verified": self.integrity_verified,
            "evidence_ref": self.evidence_ref,
            "authority": self.authority,
            "content_hash": self.content_hash,
            "notes": self.notes,
        }


class ContextVerification:
    """Correctness/completeness check + integrity gate + provenance."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-123",
        producer: str = "context.verification",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer
        self._integrity = IntegrityChecker()

    def verify(
        self,
        context: BuiltContext,
        *,
        min_chunks: int = 1,
        policy_ref: str = "pol-context-verify",
    ) -> VerificationResult:
        notes: list[str] = []
        # 1. Schema: every chunk must carry a content_hash.
        for c in context.assembled_chunks:
            if not c.content_hash:
                notes.append(f"chunk missing content_hash: {c.chunk[:20]}")
        # 2. Budget: must be within budget.
        if not context.within_budget:
            notes.append("context exceeds budget")
        # 3. Relevance: enough chunks.
        if len(context.assembled_chunks) < min_chunks:
            notes.append(f"too few chunks: {len(context.assembled_chunks)} < {min_chunks}")
        # 4. Secret isolation.
        for c in context.assembled_chunks:
            if SecretBoundary.is_secret_path(c.source):
                notes.append("secret chunk present")
        # 5. Integrity gate (T078): the built context hash must match the
        #    stored evidence's content_hash (tamper-evident provenance).
        integrity_verified = self._check_integrity(context)
        # Verdict (fail-closed).
        if notes:
            verdict = VerificationVerdict.FAIL
        elif not integrity_verified:
            verdict = VerificationVerdict.INCONCLUSIVE
        else:
            verdict = VerificationVerdict.PASS
        canonical = f"{verdict.value}|{context.content_hash}"
        content_hash = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="verification",
            source="verify",
            content=canonical,
        )
        return VerificationResult(
            built_context_ref=context.evidence_ref,
            verification_result=verdict,
            integrity_verified=integrity_verified,
            evidence_ref=evidence_ref,
            authority="aios",
            content_hash=content_hash,
            notes=notes,
        )

    def _check_integrity(self, context: BuiltContext) -> bool:
        if not context.content_hash or not context.evidence_ref:
            return False
        try:
            ev = self._store.get(context.evidence_ref)
        except Exception:
            return False
        return ev.content_hash == context.content_hash
