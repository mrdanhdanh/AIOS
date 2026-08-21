"""Tests for ExecutionPlan — AC-010-05/06 (TASK-010)."""

import pytest

from aios.orchestrator.execution_plan import ExecutionPlan, ExecutionPlanError, PlanEdge, PlanNode


class TestExecutionPlan:
    def test_valid_plan(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        plan.add_node(PlanNode(id="b", capability="cap_b"))
        plan.add_edge(PlanEdge(from_id="a", to_id="b"))
        plan.validate()
        assert plan.is_valid

    def test_empty_plan_reject(self):
        plan = ExecutionPlan(plan_id="p1")
        with pytest.raises(ExecutionPlanError):
            plan.validate()

    def test_duplicate_node_reject(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        with pytest.raises(ExecutionPlanError):
            plan.add_node(PlanNode(id="a", capability="cap_b"))

    def test_edge_unknown_node_reject(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        with pytest.raises(ExecutionPlanError):
            plan.add_edge(PlanEdge(from_id="a", to_id="b"))

    def test_cycle_reject(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        plan.add_node(PlanNode(id="b", capability="cap_b"))
        plan.add_edge(PlanEdge(from_id="a", to_id="b"))
        plan.add_edge(PlanEdge(from_id="b", to_id="a"))
        with pytest.raises(ExecutionPlanError, match="cycle"):
            plan.validate()

    def test_invalid_permission_reject(self):
        plan = ExecutionPlan(plan_id="p1", permissions=["invalid.perm"])
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        with pytest.raises(ExecutionPlanError):
            plan.validate()

    def test_invalid_resource_reject(self):
        plan = ExecutionPlan(plan_id="p1", resources={"cpu": -1})
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        with pytest.raises(ExecutionPlanError):
            plan.validate()

    def test_to_dict(self):
        plan = ExecutionPlan(plan_id="p1")
        plan.add_node(PlanNode(id="a", capability="cap_a"))
        d = plan.to_dict()
        assert d["plan_id"] == "p1"
        assert len(d["nodes"]) == 1

    def test_self_loop_reject(self):
        with pytest.raises(ExecutionPlanError):
            PlanEdge(from_id="a", to_id="a").validate()
