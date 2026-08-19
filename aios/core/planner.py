"""Execution plan primitives.

Lightweight data structures that later planning tasks (TASK-010, TASK-026)
extend into a full execution pipeline.

Example::

    from aios.core.planner import ExecutionPlan, Step, StepStatus

    plan = ExecutionPlan(plan_id="plan-1")
    step = Step(step_id="s1", action="validate")
    plan.add_step(step)
    step.transition(StepStatus.RUNNING)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

__all__ = ["ExecutionPlan", "Step", "StepStatus", "PlanError"]


class PlanError(Exception):
    """Raised on invalid plan operations."""


class StepStatus(Enum):
    """Lifecycle of a single execution step."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


# Valid status transitions (source -> set of valid targets).
_TRANSITIONS: Dict[StepStatus, Set[StepStatus]] = {
    StepStatus.PENDING: {StepStatus.RUNNING, StepStatus.SKIPPED, StepStatus.CANCELLED},
    StepStatus.RUNNING: {StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.CANCELLED},
    StepStatus.COMPLETED: set(),
    StepStatus.FAILED: set(),
    StepStatus.SKIPPED: set(),
    StepStatus.CANCELLED: set(),
}


@dataclass
class Step:
    """A single step in an execution plan.

    Mutable: use :meth:`transition` to change status.
    """

    step_id: str
    action: str
    status: StepStatus = StepStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def transition(self, target: StepStatus) -> None:
        """Transition to *target* status if valid."""
        allowed = _TRANSITIONS.get(self.status, set())
        if target not in allowed:
            raise PlanError(
                f"Cannot transition from {self.status.value} to {target.value}"
            )
        now = datetime.now(timezone.utc).isoformat()
        self.status = target
        if target == StepStatus.RUNNING:
            self.started_at = now
        elif target in (StepStatus.COMPLETED, StepStatus.FAILED):
            self.completed_at = now

    @property
    def is_terminal(self) -> bool:
        """True if this step cannot transition further."""
        return self.status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED, StepStatus.CANCELLED)


@dataclass
class ExecutionPlan:
    """An ordered collection of steps forming a plan."""

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[Step] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_step(self, step: Step) -> None:
        """Append a step; rejects duplicate step IDs."""
        if any(s.step_id == step.step_id for s in self.steps):
            raise PlanError(f"Duplicate step_id: {step.step_id!r}")
        self.steps.append(step)

    def get_step(self, step_id: str) -> Step:
        """Return the step with the given ID."""
        for s in self.steps:
            if s.step_id == step_id:
                return s
        raise PlanError(f"Step not found: {step_id!r}")

    @property
    def pending_steps(self) -> List[Step]:
        return [s for s in self.steps if s.status == StepStatus.PENDING]

    @property
    def completed_steps(self) -> List[Step]:
        return [s for s in self.steps if s.status == StepStatus.COMPLETED]

    @property
    def failed_steps(self) -> List[Step]:
        return [s for s in self.steps if s.status == StepStatus.FAILED]

    @property
    def is_complete(self) -> bool:
        """True when all steps are in a terminal state."""
        return all(s.is_terminal for s in self.steps)

    @property
    def has_failures(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps)

    def summary(self) -> Dict[str, Any]:
        """Return a human-readable summary dict."""
        counts: Dict[str, int] = {}
        for s in self.steps:
            counts[s.status.value] = counts.get(s.status.value, 0) + 1
        return {
            "plan_id": self.plan_id,
            "total_steps": len(self.steps),
            "status_counts": counts,
            "is_complete": self.is_complete,
            "has_failures": self.has_failures,
        }
