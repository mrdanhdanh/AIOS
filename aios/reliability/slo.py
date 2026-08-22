"""SLO metrics, error budgets and burn-rate guard (TASK-069).

Fail-closed: when an error budget is exhausted the system must degrade safely or
stop accepting new work — it must NOT continue as if healthy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class SLOStatus(str, Enum):
    """Aggregate SLO status."""

    HEALTHY = "HEALTHY"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"


@dataclass
class SLOMetric:
    """A service-level objective metric for a critical path."""

    name: str
    objective: str  # e.g. "99.5% success"
    window: str  # e.g. "24h"
    current: float = 1.0  # current success ratio in [0, 1]
    error_budget_remaining: float = 1.0  # remaining budget in [0, 1]
    evidence_ref: Optional[str] = None


@dataclass
class ErrorBudget:
    """A burn-rate guarded error budget (fail-closed when exhausted)."""

    total: float = 1.0
    remaining: float = 1.0
    burn_rate_threshold: float = 1.0

    def burn(self, amount: float) -> None:
        self.remaining = max(0.0, self.remaining - amount)

    def is_exhausted(self) -> bool:
        return self.remaining <= 0.0

    def guard(self) -> None:
        """Fail-closed: refuse to continue normally when the budget is gone."""
        if self.is_exhausted():
            raise ErrorBudgetExhausted(
                "error budget exhausted: degrade safe / stop new work (fail-closed)"
            )


class ErrorBudgetExhausted(Exception):
    """Raised when an error budget is exhausted (fail-closed degrade/stop)."""


class SLORegistry:
    """Registry of SLO metrics with error-budget tracking."""

    def __init__(self) -> None:
        self._metrics: Dict[str, SLOMetric] = {}
        self._budgets: Dict[str, ErrorBudget] = {}
        self._total: Dict[str, float] = {}
        self._failures: Dict[str, float] = {}

    def register(self, metric: SLOMetric) -> None:
        self._metrics[metric.name] = metric
        if metric.name not in self._budgets:
            self._budgets[metric.name] = ErrorBudget(
                total=1.0, remaining=metric.error_budget_remaining
            )
            self._total[metric.name] = 0.0
            self._failures[metric.name] = 0.0

    def get(self, name: str) -> SLOMetric:
        return self._metrics[name]

    def record(self, name: str, success: bool, weight: float = 1.0) -> None:
        """Record an outcome and recompute the error budget (deterministic)."""
        metric = self._metrics[name]
        budget = self._budgets[name]
        self._total[name] += weight
        if not success:
            self._failures[name] += weight
        total = self._total[name]
        failures = self._failures[name]
        metric.current = (total - failures) / total if total else 1.0
        budget.remaining = max(0.0, 1.0 - failures / total)
        metric.error_budget_remaining = budget.remaining

    def error_budget_remaining(self, name: str) -> float:
        return self._budgets[name].remaining

    def is_exhausted(self, name: str) -> bool:
        return self._budgets[name].is_exhausted()

    def guard(self, name: str) -> None:
        """Fail-closed guard for a named SLO."""
        self._budgets[name].guard()
