"""TASK-178 — Exception Management (M24).

Manages exception lifecycle deterministically. Fail-closed: an exception with no
justification is REJECTED; UNKNOWN is never promoted to APPROVED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

VALID_STATES = ("PENDING", "APPROVED", "REJECTED", "EXPIRED")


@dataclass(frozen=True)
class ExceptionRequest:
    exception_id: str
    policy_ref: str
    justification: str
    state: str = "PENDING"

    def __post_init__(self) -> None:
        if not self.exception_id:
            raise QualityGateError("exception_id must be non-empty")
        if not self.policy_ref:
            raise QualityGateError("policy_ref must be non-empty")
        if self.state not in VALID_STATES:
            raise QualityGateError(f"invalid state: {self.state}")


@dataclass(frozen=True)
class ExceptionReport:
    report_id: str
    exception_ref: str
    state: str
    reason: str


class ExceptionManager:
    """Manage exception lifecycle deterministically."""

    def request(self, req: ExceptionRequest) -> ExceptionReport:
        if not isinstance(req, ExceptionRequest):
            raise QualityGateError("req must be an ExceptionRequest")
        # Fail-closed: no justification -> REJECTED.
        if not req.justification or not req.justification.strip():
            state = "REJECTED"
            reason = "missing justification"
        else:
            state = req.state if req.state != "PENDING" else "APPROVED"
            reason = "justified"
        report_id = _hash(f"{req.exception_id}|{state}")
        return ExceptionReport(report_id=report_id, exception_ref=req.exception_id, state=state, reason=reason)
