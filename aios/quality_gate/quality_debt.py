"""TASK-179 — Quality Debt Tracking (M24).

Tracks quality debt items and classifies health. Deterministic thresholds;
fail-closed on invalid severity or negative age.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

DEBT_SEVERITY = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
DEBT_THRESHOLD = 3  # count of HIGH/CRITICAL items that breach


@dataclass(frozen=True)
class DebtItem:
    item_id: str
    severity: str
    age_days: int

    def __post_init__(self) -> None:
        if not self.item_id:
            raise QualityGateError("item_id must be non-empty")
        if self.severity not in DEBT_SEVERITY:
            raise QualityGateError(f"invalid severity: {self.severity}")
        if self.age_days < 0:
            raise QualityGateError("age_days must be non-negative")


@dataclass(frozen=True)
class DebtReport:
    report_id: str
    total: int
    critical_count: int
    status: str  # HEALTHY | AT_RISK | BREACH


class QualityDebtTracker:
    """Track quality debt and classify health."""

    def track(self, items: List[DebtItem]) -> DebtReport:
        if items is None:
            raise QualityGateError("items must be provided")
        for it in items:
            if not isinstance(it, DebtItem):
                raise QualityGateError("each item must be a DebtItem")
        total = len(items)
        critical = sum(1 for it in items if it.severity in ("HIGH", "CRITICAL"))
        if critical == 0:
            status = "HEALTHY"
        elif critical <= DEBT_THRESHOLD:
            status = "AT_RISK"
        else:
            status = "BREACH"
        report_id = _hash(f"{total}|{critical}|{status}")
        return DebtReport(report_id=report_id, total=total, critical_count=critical, status=status)
