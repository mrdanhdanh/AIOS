"""Goal state machine — enforces valid lifecycle transitions (fail-closed)."""

from __future__ import annotations

from aios.autonomous_goal.contracts import GoalState

# Allowed transitions per state.
_TRANSITIONS: dict[GoalState, set[GoalState]] = {
    GoalState.DRAFT: {GoalState.ACTIVE, GoalState.CANCELLED},
    GoalState.ACTIVE: {GoalState.PAUSED, GoalState.BLOCKED, GoalState.COMPLETED, GoalState.FAILED, GoalState.CANCELLED},
    GoalState.PAUSED: {GoalState.ACTIVE, GoalState.CANCELLED, GoalState.EXPIRED},
    GoalState.BLOCKED: {GoalState.ACTIVE, GoalState.FAILED, GoalState.CANCELLED},
    GoalState.COMPLETED: set(),
    GoalState.FAILED: {GoalState.DRAFT},
    GoalState.CANCELLED: set(),
    GoalState.EXPIRED: set(),
}


class GoalStateMachine:
    """Validates goal lifecycle transitions."""

    def can_transition(self, current: GoalState, target: GoalState) -> bool:
        return target in _TRANSITIONS.get(current, set())

    def transition(self, current: GoalState, target: GoalState) -> GoalState:
        if not self.can_transition(current, target):
            raise ValueError(f"Illegal goal transition: {current.value} -> {target.value}")
        return target
