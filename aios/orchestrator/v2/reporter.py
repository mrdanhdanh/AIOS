"""Goal Reporter — reflects true goal state.

AC-022-07: Goal report reflects true state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GoalStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class GoalReport:
    """Report on a goal's true state."""

    goal_id: str
    title: str
    status: GoalStatus
    progress: float = 0.0
    tasks_completed: int = 0
    tasks_total: int = 0
    last_updated: float = field(default_factory=time.time)
    executions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "status": self.status.value,
            "progress": self.progress,
            "tasks_completed": self.tasks_completed,
            "tasks_total": self.tasks_total,
            "last_updated": self.last_updated,
            "executions": self.executions,
        }


class GoalReporter:
    """Reports true goal state from backend data.

    AC-022-07: Goal report reflects true state.
    """

    def __init__(self) -> None:
        self._goals: dict[str, GoalReport] = {}

    def register_goal(self, goal_id: str, title: str, tasks_total: int = 0) -> GoalReport:
        """Register a goal for tracking."""
        report = GoalReport(
            goal_id=goal_id,
            title=title,
            status=GoalStatus.ACTIVE,
            tasks_total=tasks_total,
        )
        self._goals[goal_id] = report
        return report

    def update_progress(
        self,
        goal_id: str,
        tasks_completed: int,
        execution_id: str = "",
    ) -> GoalReport | None:
        """Update goal progress."""
        report = self._goals.get(goal_id)
        if report is None:
            return None
        report.tasks_completed = tasks_completed
        if report.tasks_total > 0:
            report.progress = tasks_completed / report.tasks_total
        if execution_id and execution_id not in report.executions:
            report.executions.append(execution_id)
        report.last_updated = time.time()

        # Check if completed
        if report.tasks_total > 0 and report.tasks_completed >= report.tasks_total:
            report.status = GoalStatus.COMPLETED
            report.progress = 1.0

        return report

    def fail_goal(self, goal_id: str) -> GoalReport | None:
        report = self._goals.get(goal_id)
        if report is None:
            return None
        report.status = GoalStatus.FAILED
        report.last_updated = time.time()
        return report

    def get_goal(self, goal_id: str) -> GoalReport | None:
        return self._goals.get(goal_id)

    def list_goals(self) -> list[GoalReport]:
        return list(self._goals.values())

    def active_goals(self) -> list[GoalReport]:
        return [g for g in self._goals.values() if g.status == GoalStatus.ACTIVE]
