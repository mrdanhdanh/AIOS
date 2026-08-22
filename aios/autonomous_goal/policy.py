"""Autonomy boundary — gates goal actions by autonomy level (fail-closed)."""

from __future__ import annotations

from enum import Enum

from aios.autonomous_goal.contracts import GoalState


class AutonomyLevel(str, Enum):
    SUPERVISED = "supervised"
    ASSISTED = "assisted"
    AUTONOMOUS = "autonomous"


class AutonomyBoundary:
    """Decides whether a goal may auto-transition without human approval."""

    def __init__(self, level: AutonomyLevel = AutonomyLevel.ASSISTED) -> None:
        self.level = level

    def may_auto_transition(self, target: GoalState) -> bool:
        """Fail-closed: only AUTONOMOUS may self-complete/fail without approval."""
        if target in (GoalState.COMPLETED, GoalState.FAILED, GoalState.CANCELLED):
            return self.level == AutonomyLevel.AUTONOMOUS
        return True

    def requires_approval(self, target: GoalState) -> bool:
        return not self.may_auto_transition(target)
