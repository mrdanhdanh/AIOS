"""Tests for TASK-051 Autonomous Planner."""
from __future__ import annotations

from aios.autonomous_planner.contracts import (
    AutonomousPlan,
    PlanStatus,
    PlanTask,
    ReplanSafety,
    ReplanTrigger,
)
from aios.autonomous_planner.planner import AutonomousPlanner, PlannerContext
from aios.autonomous_planner.validation import PlanValidator, ValidationStage


def _ctx(goal_id="g1", caps=("read", "write"), prev=None):
    return PlannerContext(goal_id=goal_id, available_capabilities=list(caps), previous_plan=prev)


def test_rule_based_plan_generated_without_llm():
    p = AutonomousPlanner()
    plan = p.plan("Build a feature", _ctx())
    assert plan.status == PlanStatus.VALID
    assert p.llm_call_count == 0
    assert len(plan.tasks) >= 1


def test_deterministic_first_no_llm_for_template():
    p = AutonomousPlanner()
    tpl = AutonomousPlan(objective="deploy service", tasks=[PlanTask(name="d")])
    p.register_template("deploy", tpl)
    plan = p.plan("please deploy the service now", _ctx())
    assert plan.status == PlanStatus.VALID
    assert p.llm_call_count == 0
    assert plan.tasks[0].name == "d"


def test_llm_only_when_needed():
    p = AutonomousPlanner()
    calls = {"n": 0}

    def llm(obj, ctx):
        calls["n"] += 1
        return AutonomousPlan(objective=obj, tasks=[PlanTask(name="llm")],
                              required_capabilities=list(ctx.available_capabilities))

    plan = p.plan("completely novel objective xyz", _ctx(), llm_planner=llm)
    assert calls["n"] == 1
    assert p.llm_call_count == 1
    assert plan.tasks[0].name == "llm"


def test_validation_rejects_unknown_capability():
    v = PlanValidator(available_capabilities=["read"])
    plan = AutonomousPlan(goal_id="g", objective="o",
                          tasks=[PlanTask(name="t", required_capabilities=["network"])])
    res = v.validate(plan)
    assert not res.valid
    assert res.stage == ValidationStage.CAPABILITY


def test_validation_rejects_cycle():
    v = PlanValidator()
    t1 = PlanTask(name="a")
    t2 = PlanTask(name="b", depends_on=[t1.task_id])
    t1.depends_on = [t2.task_id]
    plan = AutonomousPlan(goal_id="g", objective="o", tasks=[t1, t2])
    res = v.validate(plan)
    assert not res.valid
    assert res.stage == ValidationStage.EXECUTION_GRAPH


def test_validation_rejects_side_effect_without_permission():
    v = PlanValidator(granted_permissions=["read"])
    plan = AutonomousPlan(goal_id="g", objective="o",
                          tasks=[PlanTask(name="t", side_effect=True)])
    res = v.validate(plan)
    assert not res.valid
    assert res.stage == ValidationStage.PERMISSION


def test_replan_safety_requires_approval_for_policy_change():
    p = AutonomousPlanner()
    safety = p.classify_replan_safety(ReplanTrigger.POLICY_CHANGED, _ctx(), autonomy_level="supervised")
    assert safety == ReplanSafety.REQUIRES_HUMAN_APPROVAL


def test_replan_safety_safe_for_transient_failure():
    p = AutonomousPlanner()
    safety = p.classify_replan_safety(ReplanTrigger.TASK_FAILED, _ctx())
    assert safety == ReplanSafety.SAFE_TO_REPLAN


def test_replan_creates_new_version():
    p = AutonomousPlanner()
    prev = p.plan("objective", _ctx())
    ctx = _ctx(prev=prev)
    ctx.goal_state = {"objective": "objective"}
    decision = p.replan(ReplanTrigger.TASK_FAILED, ctx)
    assert decision.new_plan is not None
    assert decision.new_plan.version == prev.version + 1
    assert decision.new_plan.parent_plan_id == prev.plan_id
    assert prev.status == PlanStatus.SUPERSEDED


def test_replan_blocked_returns_no_plan():
    p = AutonomousPlanner()
    decision = p.replan(ReplanTrigger.MANUAL, _ctx(), )
    # manual -> requires human approval, no auto plan
    assert decision.new_plan is None
    assert decision.safety == ReplanSafety.REQUIRES_HUMAN_APPROVAL
