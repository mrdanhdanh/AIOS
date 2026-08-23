"""Verification Gate (TASK-151, M21).

Verifies loop output (T150) before promoting PASS, fail-closed, on Verification
Engine T142 + Verification Integrity T078. Built on Progress/Regression Detection
T150 + Evidence T001. TASK-151 is a *gate*, not a new verifier.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.progress_detection import ProgressReport


class VerifyStatus(str, Enum):
    """Verification outcome (T151)."""

    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class VerificationResult:
    """Immutable-by-id verification result (T151)."""

    result_id: str
    progress_ref: str
    verification_result: VerifyStatus
    integrity_verified: bool
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.result_id:
            raise CodingLoopError("result_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("VerificationResult requires evidence_ref (T001 Rule 5).")


class VerificationGate:
    """Fail-closed verification gate (T151)."""

    def __init__(self) -> None:
        self._results: Dict[str, VerificationResult] = {}

    def verify(
        self,
        progress_report: ProgressReport,
        output_hash: str,
        integrity_verified: bool = True,
        evidence_ref: Optional[str] = None,
        result_id: Optional[str] = None,
    ) -> VerificationResult:
        # Fail-closed: verification requires a progress report with provenance (T001 Rule 5).
        if progress_report is None or not progress_report.evidence_ref:
            raise CodingLoopError("Verify requires progress report with provenance (T001 Rule 5).")
        # Fail-closed: cannot verify without an output hash -> INCONCLUSIVE (T078).
        if not output_hash:
            status = VerifyStatus.INCONCLUSIVE
            integrity = False
        else:
            # Deterministic: regression -> FAIL; otherwise PASS.
            if progress_report.regression_flag:
                status = VerifyStatus.FAIL
                integrity = integrity_verified
            else:
                status = VerifyStatus.PASS
                integrity = integrity_verified
        ev = evidence_ref or progress_report.evidence_ref
        rid = result_id or f"ver-{uuid.uuid4().hex[:12]}"
        if rid in self._results:
            raise CodingLoopError(f"Duplicate result_id '{rid}' (T001 Rule 1).")
        res = VerificationResult(
            result_id=rid,
            progress_ref=progress_report.report_id,
            verification_result=status,
            integrity_verified=integrity,
            evidence_ref=ev,
        )
        self._results[rid] = res
        return res

    def is_promotable(self, result: VerificationResult) -> bool:
        """FAIL/INCONCLUSIVE is never promoted to PASS (fail-closed, T078)."""
        return result.verification_result == VerifyStatus.PASS and result.integrity_verified

    def get(self, result_id: str) -> VerificationResult:
        if result_id not in self._results:
            raise CodingLoopError(f"Unknown result '{result_id}'.")
        return self._results[result_id]

    def provenance(self, result_id: str) -> dict:
        res = self.get(result_id)
        payload = (
            f"{res.result_id}|{res.progress_ref}|{res.verification_result.value}|"
            f"{res.integrity_verified}|{res.evidence_ref}"
        )
        return {
            "result_id": res.result_id,
            "progress_ref": res.progress_ref,
            "verification_result": res.verification_result.value,
            "integrity_verified": res.integrity_verified,
            "evidence_ref": res.evidence_ref,
            "authority": res.authority,
            "content_hash": _hash(payload),
        }
