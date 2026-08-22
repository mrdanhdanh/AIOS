"""AutonomousGoalEngine."""
from __future__ import annotations

import time

from aios.autonomous_goal.contracts import (
    Goal,
    GoalEvidence,
    GoalPlan,
    GoalState,
    GoalStatus,
)
from aios.autonomous_goal.policy import AutonomyBoundary, AutonomyLevel
from aios.autonomous_goal.state_machine import GoalStateMachine


class ProgressObserver:
    """Observes goal progress (objectives completed / state)."""

    def snapshot(self, goal: Goal) -> dict:
        total = len(goal.objectives)
        done = sum(1 for o in goal.objectives if o.done)
        return {
            "goal_id": goal.goal_id,
            "state": goal.state.value,
            "objectives_total": total,
            "objectives_done": done,
            "progress": (done / total) if total else 0.0,
        }


class AutonomousGoalEngine:
    def __init__(self, autonomy: AutonomyLevel = AutonomyLevel.ASSISTED) -> None:
        self._goals: dict[str, Goal] = {}
        self._plans: dict[str, GoalPlan] = {}
        self._fsm = GoalStateMachine()
        self._boundary = AutonomyBoundary(autonomy)
        self._observer = ProgressObserver()

    def create_goal(self, title: str, description: str = "") -> Goal:
        g = Goal(title=title, description=description)
        self._goals[g.goal_id] = g
        return g

    def add_objective(self, goal_id: str, title: str, parent_id: str = "") -> Goal:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        from aios.autonomous_goal.contracts import Objective
        g.objectives.append(Objective(title=title, parent_id=parent_id))
        return g

    def plan_goal(self, goal_id: str, steps: list[str]) -> GoalPlan:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        g.status = GoalStatus.PLANNING
        plan = GoalPlan(goal_id=goal_id, steps=steps)
        self._plans[plan.plan_id] = plan
        # Transition DRAFT -> ACTIVE via the state machine.
        g.state = self._fsm.transition(g.state, GoalState.ACTIVE)
        g.status = GoalStatus.EXECUTING
        self._record_evidence(g, "plan")
        return plan

    def complete_goal(self, goal_id: str) -> Goal:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        if self._boundary.requires_approval(GoalState.COMPLETED):
            raise RuntimeError("Completion requires human approval at this autonomy level")
        g.state = self._fsm.transition(g.state, GoalState.COMPLETED)
        g.status = GoalStatus.COMPLETED
        self._record_evidence(g, "complete")
        return g

    def fail_goal(self, goal_id: str) -> Goal:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        if self._boundary.requires_approval(GoalState.FAILED):
            raise RuntimeError("Failure requires human approval at this autonomy level")
        g.state = self._fsm.transition(g.state, GoalState.FAILED)
        g.status = GoalStatus.FAILED
        self._record_evidence(g, "fail")
        return g

    def pause_goal(self, goal_id: str) -> Goal:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        g.state = self._fsm.transition(g.state, GoalState.PAUSED)
        g.status = GoalStatus.PAUSED
        return g

    def resume_goal(self, goal_id: str) -> Goal:
        """Resume a paused goal (state preserved)."""
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        g.state = self._fsm.transition(g.state, GoalState.ACTIVE)
        g.status = GoalStatus.EXECUTING
        self._record_evidence(g, "resume")
        return g

    def progress(self, goal_id: str) -> dict:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        return self._observer.snapshot(g)

    def _record_evidence(self, goal: Goal, action: str) -> None:
        goal.evidence.append(GoalEvidence(goal_id=goal.goal_id, action=action,
                                          provenance=[f"goal:{goal.goal_id}:{action}"]))

    def list_goals(self) -> list[Goal]: return list(self._goals.values())
    def get_goal(self, gid: str) -> Goal | None: return self._goals.get(gid)
    def get_plan(self, pid: str) -> GoalPlan | None: return self._plans.get(pid)
