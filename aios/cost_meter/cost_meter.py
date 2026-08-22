"""Cost metering per step/goal with a fail-closed budget guard (TASK-075)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CostExceeded(Exception):
    """Fail-closed signal emitted when cumulative cost exceeds the budget.

    Integration note: if ``aios.autonomy_safety`` (SAFE_STOP) or
    ``aios.kill_switch`` were available they would be invoked here; absent those
    modules we emit ``CostExceeded`` so callers can escalate/stop.
    """


@dataclass
class CostRecord:
    """A single metered cost event with provenance."""

    goal_id: str
    step_id: str
    amount: float
    provider: str
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "step_id": self.step_id,
            "amount": self.amount,
            "provider": self.provider,
            "evidence_ref": self.evidence_ref,
        }


class CostMeter:
    """Meters cost per step/goal and enforces a budget (fail-closed).

    Every :meth:`record` carries an ``evidence_ref`` for provenance (AC6). When
    cumulative spend exceeds ``budget`` the meter raises :class:`CostExceeded`
    (escalate/stop) — never silently over-spends.
    """

    def __init__(self, budget: float, goal_id: str = "", on_exceed: str = "stop") -> None:
        if budget < 0:
            raise ValueError("budget must be non-negative")
        self._budget = float(budget)
        self._goal_id = goal_id
        self._on_exceed = on_exceed  # "stop" (raise) or "escalate"
        self._spent = 0.0
        self._records: list[CostRecord] = []

    def record(
        self,
        step_id: str,
        amount: float,
        provider: str,
        evidence_ref: str = "",
    ) -> CostRecord:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        # Fail-closed: reject the step *before* counting it, so spend never
        # silently grows past the budget (escalate/stop).
        if self._spent + amount > self._budget:
            raise CostExceeded(
                f"Cost {self._spent + amount:.6f} would exceed budget "
                f"{self._budget:.6f} for goal '{self._goal_id}' "
                f"(on_exceed={self._on_exceed})"
            )
        self._spent += amount
        rec = CostRecord(self._goal_id, step_id, amount, provider, evidence_ref)
        self._records.append(rec)
        return rec

    def spent(self) -> float:
        return self._spent

    def remaining(self) -> float:
        return max(0.0, self._budget - self._spent)

    def is_over_budget(self) -> bool:
        return self._spent > self._budget

    def budget(self) -> float:
        return self._budget

    def records(self) -> list[CostRecord]:
        return list(self._records)
