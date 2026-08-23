"""TASK-161 — Performance Verifier (M22).

Deterministic performance budget check: observed must be within limit.
Fail-closed: a budget with no provenance (empty id) is rejected; over-budget
-> INSUFFICIENT (never promoted).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class PerfBudget:
    budget_id: str
    metric: str
    limit: float
    observed: float

    def __post_init__(self) -> None:
        if not self.budget_id:
            raise VerificationError("budget_id must be non-empty")
        if not self.metric:
            raise VerificationError("metric must be non-empty")


@dataclass(frozen=True)
class PerfReport:
    report_id: str
    budget_ref: str
    within_budget: bool
    status: str  # PASS | INSUFFICIENT


class PerformanceVerifier:
    """Verify an observed performance metric is within its budget limit."""

    def verify(self, budget: PerfBudget) -> PerfReport:
        if not isinstance(budget, PerfBudget):
            raise VerificationError("budget must be a PerfBudget")
        if not budget.budget_id:
            raise VerificationError("budget_id must be non-empty (provenance)")

        within = budget.observed <= budget.limit
        status = "PASS" if within else "INSUFFICIENT"
        report_id = _hash(f"{budget.budget_id}|{within}")
        return PerfReport(
            report_id=report_id,
            budget_ref=budget.budget_id,
            within_budget=within,
            status=status,
        )
