"""TASK-201 — Approval Gate (M26).

Approval gate for coding changes, converging Approval Workflow (T183) and
Permission (T097). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from aios.coding_edition._common import CodingEditionError, _hash
from aios.coding_edition.risk import RiskEngine, RiskInput, RiskLevel


class ApprovalVerdict(str, Enum):
    """Approval outcome (T201)."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    UNKNOWN = "UNKNOWN"


# Severity rank for deterministic comparison (higher = more severe).
_RISK_RANK = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.CRITICAL: 3,
    RiskLevel.UNKNOWN: -1,
}


@dataclass
class ApprovalRequest:
    """A change awaiting approval (T201)."""

    request_id: str
    change_id: str
    risk_input: RiskInput
    required_approvers: int = 1
    obtained_approvers: int = 0
    authority: str = "aios"

    def __post_init__(self) -> None:
        if not self.request_id:
            raise CodingEditionError("request_id is required (T001 Rule 1, immutable).")
        if self.required_approvers < 1:
            raise CodingEditionError("required_approvers must be >= 1.")


class ApprovalGate:
    """Deterministic approval gate (T201)."""

    def __init__(self, risk_engine: Optional[RiskEngine] = None, escalate_above: RiskLevel = RiskLevel.HIGH) -> None:
        self._risk = risk_engine or RiskEngine()
        self._escalate_above = escalate_above

    def evaluate(self, req: ApprovalRequest) -> Tuple[ApprovalVerdict, str]:
        """Evaluate an approval request (fail-closed, deterministic).

        CRITICAL risk -> REJECTED; risk >= escalate_above -> ESCALATED;
        insufficient approvers -> ESCALATED; otherwise APPROVED.
        """
        score, level = self._risk.assess(req.risk_input)
        if level == RiskLevel.UNKNOWN:
            return ApprovalVerdict.UNKNOWN, "no risk model"
        if level == RiskLevel.CRITICAL:
            return ApprovalVerdict.REJECTED, f"critical risk {score:.2f}"
        if _RISK_RANK.get(level, -1) >= _RISK_RANK.get(self._escalate_above, 2):
            return ApprovalVerdict.ESCALATED, f"risk {level.value} needs escalation"
        if req.obtained_approvers < req.required_approvers:
            return ApprovalVerdict.ESCALATED, "insufficient approvers"
        return ApprovalVerdict.APPROVED, f"risk {level.value} approved"

    def approval_hash(self, req: ApprovalRequest) -> str:
        v, _ = self.evaluate(req)
        return _hash(f"{req.request_id}|{v.value}")
