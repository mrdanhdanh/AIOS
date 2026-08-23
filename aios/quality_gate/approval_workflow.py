"""TASK-183 — Approval Workflow + Rollback Recommendation (M24).

Submits approval requests and recommends rollback on high risk. Fail-closed:
HIGH/CRITICAL risk requires >=2 approvers, else REJECTED + rollback BLOCKED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from aios.quality_gate._common import QualityGateError, _hash

APPROVAL_STATES = ("SUBMITTED", "APPROVED", "REJECTED", "WITHDRAWN")
RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    change_ref: str
    risk_level: str
    approvers: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.request_id:
            raise QualityGateError("request_id must be non-empty")
        if not self.change_ref:
            raise QualityGateError("change_ref must be non-empty")
        if self.risk_level not in RISK_LEVELS:
            raise QualityGateError(f"invalid risk_level: {self.risk_level}")


@dataclass(frozen=True)
class ApprovalReport:
    report_id: str
    request_ref: str
    state: str
    rollback: str


class ApprovalWorkflow:
    """Submit approval requests and recommend rollback on high risk."""

    def submit(self, req: ApprovalRequest) -> ApprovalReport:
        if not isinstance(req, ApprovalRequest):
            raise QualityGateError("req must be an ApprovalRequest")
        # Fail-closed: HIGH/CRITICAL risk requires >=2 approvers.
        if req.risk_level in ("HIGH", "CRITICAL") and len(req.approvers) < 2:
            state = "REJECTED"
            rollback = "BLOCKED"
        else:
            state = "APPROVED"
            rollback = "RECOMMEND" if req.risk_level in ("HIGH", "CRITICAL") else "NO_RECOMMEND"
        report_id = _hash(f"{req.request_id}|{state}|{rollback}")
        return ApprovalReport(report_id=report_id, request_ref=req.request_id, state=state, rollback=rollback)
