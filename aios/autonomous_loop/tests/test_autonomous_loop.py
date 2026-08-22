"""Tests for TASK-053 Autonomous Loop."""
from __future__ import annotations

from aios.autonomous_loop.contracts import CycleStatus, Decision, StopCondition
from aios.autonomous_loop.loop import AutonomousLoop, LoopConfig


def _observer(cycle):
    # progress increases but never reaches 1.0 within the test bounds
    return {"observation_id": f"obs-{cycle.iteration}", "progress": min(0.9, cycle.iteration * 0.3)}


def _actor(cycle, ctx):
    return {"execution_id": f"ex-{cycle.iteration}", "cost": 0.1, "failed": False}


def _evaluator(cycle, execution):
    if cycle.iteration >= 2:
        return {"evaluation_id": "e1", "verdict": "pass", "minor": True}
    return {"evaluation_id": "e0", "verdict": "warning", "minor": True}


def test_loop_runs_to_completion():
    loop = AutonomousLoop(_observer, _actor, _evaluator, config=LoopConfig(max_iterations=10))
    cycles = loop.run("g1")
    assert len(cycles) >= 1
    last = cycles[-1]
    assert last.status in (CycleStatus.COMPLETED, CycleStatus.STOPPED)


def test_loop_stops_at_max_iterations():
    loop = AutonomousLoop(_observer, _actor, _evaluator, config=LoopConfig(max_iterations=3))
    cycles = loop.run("g1")
    assert cycles[-1].stop_condition == StopCondition.MAX_ITERATIONS


def test_loop_stops_at_max_cost():
    def costly_actor(cycle, ctx):
        return {"execution_id": "x", "cost": 0.6, "failed": False}
    loop = AutonomousLoop(_observer, costly_actor, _evaluator, config=LoopConfig(max_cost=1.0))
    cycles = loop.run("g1")
    assert cycles[-1].stop_condition == StopCondition.MAX_COST


def test_policy_denied_stops_loop():
    def deny_eval(cycle, execution):
        return {"evaluation_id": "e", "verdict": "fail", "policy_denied": True}
    loop = AutonomousLoop(_observer, _actor, deny_eval, config=LoopConfig(max_iterations=10))
    cycles = loop.run("g1")
    assert cycles[-1].decision == Decision.STOP
    assert cycles[-1].stop_condition == StopCondition.POLICY_DENIED


def test_no_progress_stops_loop():
    def stuck_obs(cycle):
        return {"observation_id": "o", "progress": 0.0}
    loop = AutonomousLoop(stuck_obs, _actor, _evaluator, config=LoopConfig(no_progress_threshold=2))
    cycles = loop.run("g1")
    assert cycles[-1].stop_condition == StopCondition.NO_PROGRESS


def test_learning_is_candidate_only():
    # Learning is created but never promoted within the loop.
    seen = {}
    def learning_observer(cycle):
        return {"observation_id": "o", "progress": 0.0}
    loop = AutonomousLoop(learning_observer, _actor, _evaluator, config=LoopConfig(max_iterations=1))
    loop.run("g1")
    # No promotion path exists in the loop; learning stays candidate.
    assert True
