"""Tests for TASK-050 Autonomous Goal Engine (state machine, objectives, policy, resume)."""

from __future__ import annotations

from aios.autonomous_goal.contracts import GoalState, GoalStatus
from aios.autonomous_goal.engine import AutonomousGoalEngine
from aios.autonomous_goal.policy import AutonomyLevel


def test_state_machine_transitions() -> None:
    eng = AutonomousGoalEngine()
    g = eng.create_goal("Build X")
    assert g.state == GoalState.DRAFT
    eng.plan_goal(g.goal_id, ["s1"])
    assert g.state == GoalState.ACTIVE
    eng.pause_goal(g.goal_id)
    assert g.state == GoalState.PAUSED
    eng.resume_goal(g.goal_id)
    assert g.state == GoalState.ACTIVE


def test_objectives_and_progress() -> None:
    eng = AutonomousGoalEngine()
    g = eng.create_goal("X")
    eng.add_objective(g.goal_id, "o1")
    eng.add_objective(g.goal_id, "o2")
    prog = eng.progress(g.goal_id)
    assert prog["objectives_total"] == 2
    assert prog["progress"] == 0.0


def test_policy_requires_approval_at_assisted() -> None:
    eng = AutonomousGoalEngine(autonomy=AutonomyLevel.ASSISTED)
    g = eng.create_goal("X")
    eng.plan_goal(g.goal_id, ["s1"])
    try:
        eng.complete_goal(g.goal_id)
        assert False, "should require approval"
    except RuntimeError:
        pass


def test_autonomous_may_complete() -> None:
    eng = AutonomousGoalEngine(autonomy=AutonomyLevel.AUTONOMOUS)
    g = eng.create_goal("X")
    eng.plan_goal(g.goal_id, ["s1"])
    eng.complete_goal(g.goal_id)
    assert g.state == GoalState.COMPLETED


def test_evidence_recorded() -> None:
    eng = AutonomousGoalEngine(autonomy=AutonomyLevel.AUTONOMOUS)
    g = eng.create_goal("X")
    eng.plan_goal(g.goal_id, ["s1"])
    assert any(e.action == "plan" for e in g.evidence)
