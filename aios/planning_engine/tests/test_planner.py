"""Tests for planning engine."""

from __future__ import annotations

import pytest

from aios.planning_engine.contracts import ExecutionPlan, PlanStatus, PlanStep, RiskLevel
from aios.planning_engine.planner import PlanningEngine


class TestPlanningEngine:
    def test_analyze_goal(self) -> None:
        engine = PlanningEngine()
        analysis = engine.analyze_goal("Build a REST API")
        assert "code_generation" in analysis.required_capabilities
        assert analysis.complexity in ("medium", "high")

    def test_analyze_simple_goal(self) -> None:
        engine = PlanningEngine()
        analysis = engine.analyze_goal("list tasks")
        assert "general" in analysis.required_capabilities

    def test_create_plan(self) -> None:
        engine = PlanningEngine()
        plan = engine.create_plan("Build a web application")
        assert plan.status == PlanStatus.VALID
        assert plan.step_count >= 1
        assert plan.plan_id

    def test_plan_has_steps(self) -> None:
        engine = PlanningEngine()
        plan = engine.create_plan("Create and test a module")
        assert plan.step_count >= 2

    def test_no_cycles(self) -> None:
        engine = PlanningEngine()
        plan = engine.create_plan("Build feature X")
        cycles = engine.detect_cycles(plan.steps)
        assert len(cycles) == 0

    def test_validate_valid_plan(self) -> None:
        engine = PlanningEngine()
        plan = engine.create_plan("Build something")
        result = engine.validate(plan)
        assert result.valid

    def test_validate_empty_plan(self) -> None:
        engine = PlanningEngine()
        plan = ExecutionPlan(plan_id="empty")
        result = engine.validate(plan)
        assert not result.valid
        assert "no steps" in result.errors[0].lower()

    def test_detect_self_loop(self) -> None:
        engine = PlanningEngine()
        steps = [PlanStep(step_id="s1", dependencies=["s1"])]
        cycles = engine.detect_cycles(steps)
        assert len(cycles) > 0

    def test_detect_dependency_cycle(self) -> None:
        engine = PlanningEngine()
        steps = [
            PlanStep(step_id="a", dependencies=["b"]),
            PlanStep(step_id="b", dependencies=["a"]),
        ]
        cycles = engine.detect_cycles(steps)
        assert len(cycles) > 0

    def test_list_plans(self) -> None:
        engine = PlanningEngine()
        engine.create_plan("Plan 1")
        engine.create_plan("Plan 2")
        assert len(engine.list_plans()) == 2

    def test_provenance(self) -> None:
        engine = PlanningEngine()
        plan = engine.create_plan("Build test")
        assert len(plan.provenance) > 0

    def test_to_dict(self) -> None:
        engine = PlanningEngine()
        plan = engine.create_plan("Build")
        d = plan.to_dict()
        assert "plan_id" in d
        assert "steps" in d
