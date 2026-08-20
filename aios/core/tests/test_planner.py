"""Tests for :mod:`aios.core.planner`."""

from __future__ import annotations

import pytest

from aios.core.planner import ExecutionPlan, PlanError, Step, StepStatus


class TestStepTransitions:
    """Verify step status transitions."""

    def test_pending_to_running(self):
        s = Step(step_id="s1", action="do")
        s.transition(StepStatus.RUNNING)
        assert s.status == StepStatus.RUNNING
        assert s.started_at is not None

    def test_running_to_completed(self):
        s = Step(step_id="s1", action="do")
        s.transition(StepStatus.RUNNING)
        s.transition(StepStatus.COMPLETED)
        assert s.status == StepStatus.COMPLETED
        assert s.completed_at is not None

    def test_running_to_failed(self):
        s = Step(step_id="s1", action="do")
        s.transition(StepStatus.RUNNING)
        s.transition(StepStatus.FAILED)
        assert s.status == StepStatus.FAILED

    def test_pending_to_skipped(self):
        s = Step(step_id="s1", action="do")
        s.transition(StepStatus.SKIPPED)
        assert s.status == StepStatus.SKIPPED

    def test_pending_to_cancelled(self):
        s = Step(step_id="s1", action="do")
        s.transition(StepStatus.CANCELLED)
        assert s.status == StepStatus.CANCELLED

    def test_invalid_transition_raises(self):
        s = Step(step_id="s1", action="do")
        with pytest.raises(PlanError, match="Cannot transition"):
            s.transition(StepStatus.COMPLETED)

    def test_terminal_step_cannot_transition(self):
        s = Step(step_id="s1", action="do")
        s.transition(StepStatus.RUNNING)
        s.transition(StepStatus.COMPLETED)
        with pytest.raises(PlanError, match="Cannot transition"):
            s.transition(StepStatus.RUNNING)

    def test_is_terminal(self):
        s = Step(step_id="s1", action="do")
        assert s.is_terminal is False
        s.transition(StepStatus.RUNNING)
        assert s.is_terminal is False
        s.transition(StepStatus.COMPLETED)
        assert s.is_terminal is True


class TestExecutionPlan:
    """Verify plan operations."""

    def test_add_step(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_step(Step(step_id="s1", action="a1"))
        assert len(plan.steps) == 1

    def test_duplicate_step_id_raises(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        with pytest.raises(PlanError, match="Duplicate step_id"):
            plan.add_step(Step(step_id="s1", action="a2"))

    def test_get_step(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        assert plan.get_step("s1").action == "a1"

    def test_get_step_not_found_raises(self):
        plan = ExecutionPlan()
        with pytest.raises(PlanError, match="Step not found"):
            plan.get_step("missing")

    def test_pending_steps(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        plan.add_step(Step(step_id="s2", action="a2"))
        plan.get_step("s1").transition(StepStatus.RUNNING)
        assert len(plan.pending_steps) == 1

    def test_completed_steps(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        plan.get_step("s1").transition(StepStatus.RUNNING)
        plan.get_step("s1").transition(StepStatus.COMPLETED)
        assert len(plan.completed_steps) == 1

    def test_failed_steps(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        plan.get_step("s1").transition(StepStatus.RUNNING)
        plan.get_step("s1").transition(StepStatus.FAILED)
        assert len(plan.failed_steps) == 1

    def test_is_complete(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        assert plan.is_complete is False
        plan.get_step("s1").transition(StepStatus.RUNNING)
        plan.get_step("s1").transition(StepStatus.COMPLETED)
        assert plan.is_complete is True

    def test_has_failures(self):
        plan = ExecutionPlan()
        plan.add_step(Step(step_id="s1", action="a1"))
        assert plan.has_failures is False
        plan.get_step("s1").transition(StepStatus.RUNNING)
        plan.get_step("s1").transition(StepStatus.FAILED)
        assert plan.has_failures is True

    def test_summary(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_step(Step(step_id="s1", action="a1"))
        s = plan.summary()
        assert s["plan_id"] == "p1"
        assert s["total_steps"] == 1
        assert s["status_counts"]["PENDING"] == 1


class TestStepVocabulary:
    """Verify canonical M1 vocabulary: Plan/Step/Dependency/Input/Output/Status."""

    def test_inputs_outputs_fields(self):
        s = Step(step_id="s1", action="x", inputs={"a": 1}, outputs={"b": 2})
        assert s.inputs == {"a": 1}
        assert s.outputs == {"b": 2}
        # defaults are empty dicts
        s2 = Step(step_id="s2", action="y")
        assert s2.inputs == {}
        assert s2.outputs == {}

    def test_dependencies_field(self):
        s = Step(step_id="s1", action="x", dependencies=["s0"])
        assert s.dependencies == ["s0"]

    def test_metadata_still_available(self):
        s = Step(step_id="s1", action="x", metadata={"k": "v"})
        assert s.metadata == {"k": "v"}
