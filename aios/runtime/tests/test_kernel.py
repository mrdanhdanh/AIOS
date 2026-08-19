"""Automated tests for the runtime kernel composition (TASK-005)."""

import pytest

from aios.core.container import Container
from aios.runtime.kernel import RuntimeKernel
from aios.runtime.execution import ExecutionOutcome
from aios.core.planner import ExecutionPlan, Step


def test_kernel_wires_all_services():
    k = RuntimeKernel()
    assert k.context is not None
    assert k.audit is not None
    assert k.artifacts is not None
    assert k.permissions is not None
    assert k.policy is not None
    assert k.scheduler is not None
    assert k.state is not None
    assert k.resources is not None
    assert k.executor is not None


def test_kernel_shares_singletons():
    k = RuntimeKernel()
    # Resolving twice yields the same instance (singleton lifetime).
    assert k.context is k.context
    assert k.policy is k.policy


def test_kernel_executor_runs_through_wiring():
    k = RuntimeKernel()
    plan = ExecutionPlan(plan_id="p1")
    plan.add_step(Step(step_id="s0", action="echo"))
    rep = k.executor.execute(plan, lambda s, c: f"ran-{s.step_id}")
    assert rep.status == ExecutionOutcome.COMPLETED
    assert rep.results["s0"].status == "COMPLETED"


def test_kernel_uses_external_container():
    c = Container()
    k = RuntimeKernel(container=c)
    # The kernel registered services into the provided container.
    assert k.container.is_registered(type(k.context))


def test_kernel_health_snapshot():
    k = RuntimeKernel()
    health = k.health()
    assert "context" in health
    assert "audit_events" in health
    assert "resources_registered" in health
