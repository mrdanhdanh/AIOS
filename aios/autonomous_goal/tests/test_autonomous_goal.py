"""Tests for autonomous goal engine."""
from __future__ import annotations
import pytest
from aios.autonomous_goal.contracts import Goal, GoalPlan, GoalStatus
from aios.autonomous_goal.engine import AutonomousGoalEngine
from aios.autonomous_goal.policy import AutonomyLevel

class TestAutonomousGoal:
    def test_create_goal(self):
        engine = AutonomousGoalEngine()
        g = engine.create_goal("Build feature X")
        assert g.title == "Build feature X"
        assert g.status == GoalStatus.CREATED
    def test_plan_goal(self):
        engine = AutonomousGoalEngine()
        g = engine.create_goal("Build X")
        plan = engine.plan_goal(g.goal_id, ["step1", "step2"])
        assert len(plan.steps) == 2
        assert g.status == GoalStatus.EXECUTING
    def test_complete_goal(self):
        engine = AutonomousGoalEngine(autonomy=AutonomyLevel.AUTONOMOUS)
        g = engine.create_goal("Task")
        engine.plan_goal(g.goal_id, ["s1"])
        engine.complete_goal(g.goal_id)
        assert g.status == GoalStatus.COMPLETED
    def test_fail_goal(self):
        engine = AutonomousGoalEngine(autonomy=AutonomyLevel.AUTONOMOUS)
        g = engine.create_goal("Task")
        engine.plan_goal(g.goal_id, ["s1"])
        engine.fail_goal(g.goal_id)
        assert g.status == GoalStatus.FAILED
    def test_not_found(self):
        engine = AutonomousGoalEngine()
        with pytest.raises(RuntimeError): engine.plan_goal("nonexistent", [])
    def test_list_goals(self):
        engine = AutonomousGoalEngine()
        engine.create_goal("A"); engine.create_goal("B")
        assert len(engine.list_goals()) == 2
    def test_to_dict(self):
        g = Goal(title="test")
        d = g.to_dict()
        assert d["title"] == "test"
