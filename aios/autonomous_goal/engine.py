"""AutonomousGoalEngine."""
from __future__ import annotations
from aios.autonomous_goal.contracts import Goal, GoalPlan, GoalStatus

class AutonomousGoalEngine:
    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}
        self._plans: dict[str, GoalPlan] = {}
    def create_goal(self, title: str, description: str = "") -> Goal:
        g = Goal(title=title, description=description)
        self._goals[g.goal_id] = g
        return g
    def plan_goal(self, goal_id: str, steps: list[str]) -> GoalPlan:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        g.status = GoalStatus.PLANNING
        plan = GoalPlan(goal_id=goal_id, steps=steps)
        self._plans[plan.plan_id] = plan
        g.status = GoalStatus.EXECUTING
        return plan
    def complete_goal(self, goal_id: str) -> Goal:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        g.status = GoalStatus.COMPLETED; return g
    def fail_goal(self, goal_id: str) -> Goal:
        g = self._goals.get(goal_id)
        if g is None: raise RuntimeError(f"Goal {goal_id!r} not found")
        g.status = GoalStatus.FAILED; return g
    def list_goals(self) -> list[Goal]: return list(self._goals.values())
    def get_goal(self, gid: str) -> Goal | None: return self._goals.get(gid)
    def get_plan(self, pid: str) -> GoalPlan | None: return self._plans.get(pid)
