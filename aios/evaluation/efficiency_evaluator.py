"""TASK-192 — Efficiency Evaluator (M25).

Evaluates observed efficiency against a budget limit. Based on Performance
Verifier T161. Fail-closed: over budget -> INSUFFICIENT; UNKNOWN never promoted.
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.evaluation._common import EvaluationError, _hash


@dataclass(frozen=True)
class EfficiencyBudget:
    budget_id: str
    observed: float
    limit: float
    unit: str = "ms"

    def __post_init__(self) -> None:
        if not self.budget_id:
            raise EvaluationError("budget_id must be non-empty")
        if self.limit < 0:
            raise EvaluationError("limit must be non-negative")


@dataclass(frozen=True)
class EfficiencyReport:
    report_id: str
    budget_ref: str
    status: str  # PASS | INSUFFICIENT


class EfficiencyEvaluator:
    """Evaluate observed efficiency against a budget limit."""

    def evaluate(self, budget: EfficiencyBudget) -> EfficiencyReport:
        if not isinstance(budget, EfficiencyBudget):
            raise EvaluationError("budget must be an EfficiencyBudget")
        within = budget.observed <= budget.limit
        status = "PASS" if within else "INSUFFICIENT"
        report_id = _hash(f"{budget.budget_id}|{status}")
        return EfficiencyReport(report_id=report_id, budget_ref=budget.budget_id, status=status)
