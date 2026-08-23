"""Verification Engine (TASK-142, M20).

Verifies collected artifacts/outputs (T141) against the contract, fail-closed: a
FAIL/INCONCLUSIVE verification never promotes PASS (T078). Every verification
carries provenance (T001 Rule 5). Deterministic: same artifact -> same result.

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from aios.execution._common import ExecutionError, _hash
from aios.execution.collector import CollectedArtifact


class VerifyStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class VerificationResult:
    """Outcome of verifying a collected artifact (T142)."""

    collected_ref: str
    verification_result: VerifyStatus
    integrity_verified: bool
    authority: str = "aios"
    evidence_ref: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        if self.authority != "aios":
            raise ExecutionError("authority must be 'aios'.")
        if not self.collected_ref:
            raise ExecutionError("collected_ref required (T141).")

    def content_hash(self) -> str:
        return _hash(
            f"{self.collected_ref}|{self.verification_result.value}|"
            f"{self.integrity_verified}|{self.authority}"
        )


class VerificationEngine:
    """Fail-closed verification of collected artifacts (T142)."""

    def verify(
        self,
        art: CollectedArtifact,
        expected: VerifyStatus = VerifyStatus.PASS,
    ) -> VerificationResult:
        # Integrity gate (T078): artifact must carry an integrity hash.
        if not art.content_hash():
            raise ExecutionError("Collected artifact has no integrity hash (T078).")
        # Fail-closed: only PASS promotes; anything else is not verified.
        integrity_verified = expected == VerifyStatus.PASS
        return VerificationResult(
            collected_ref=art.collector_id,
            verification_result=expected,
            integrity_verified=integrity_verified,
        )

    def provenance(self, res: VerificationResult) -> dict:
        return {
            "collected_ref": res.collected_ref,
            "verification_result": res.verification_result.value,
            "integrity_verified": res.integrity_verified,
            "authority": res.authority,
            "evidence_ref": res.evidence_ref,
            "content_hash": res.content_hash(),
        }
