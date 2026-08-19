"""Automated tests for the runtime execution service (TASK-005)."""

import threading

import pytest

from aios.core.events import EventBus
from aios.core.planner import ExecutionPlan, Step, StepStatus
from aios.runtime.execution import (
    ExecutionOutcome,
    ExecutionReport,
    Executor,
    StepResult,
)
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope


def _plan(actions):
    plan = ExecutionPlan(plan_id="p1")
    for i, a in enumerate(actions):
        plan.add_step(Step(step_id=f"s{i}", action=a))
    return plan


def test_execute_completes_all_steps():
    ex = Executor()
    plan = _plan(["a", "b", "c"])
    calls = []

    def handler(step, ctx):
        calls.append(step.step_id)
        return f"out-{step.step_id}"

    rep = ex.execute(plan, handler)
    assert rep.status == ExecutionOutcome.COMPLETED
    assert calls == ["s0", "s1", "s2"]
    assert all(r.status == "COMPLETED" for r in rep.results.values())


def test_execute_retries_on_error():
    ex = Executor()
    plan = _plan(["flaky"])
    attempts = {"n": 0}

    def handler(step, ctx):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ValueError("boom")
        return "ok"

    rep = ex.execute(plan, handler, max_attempts=3)
    assert rep.status == ExecutionOutcome.COMPLETED
    assert attempts["n"] == 3
    assert rep.results["s0"].attempts == 3


def test_execute_fails_after_retries():
    ex = Executor()
    plan = _plan(["bad"])

    def handler(step, ctx):
        raise RuntimeError("always fails")

    rep = ex.execute(plan, handler, max_attempts=2)
    assert rep.status == ExecutionOutcome.FAILED
    assert rep.results["s0"].attempts == 2
    assert "always fails" in (rep.results["s0"].error or "")


def test_execute_timeout_marks_timeout():
    ex = Executor()
    plan = _plan(["slow"])

    def handler(step, ctx):
        import time

        time.sleep(0.5)
        return "done"

    rep = ex.execute(plan, handler, timeout=0.1)
    assert rep.status == ExecutionOutcome.TIMEOUT
    assert rep.results["s0"].status == "TIMEOUT"


def test_execute_policy_deny_blocks():
    broker = PermissionBroker()
    eng = PolicyEngine(broker=broker)  # no grants -> any scoped request denied
    ex = Executor(policy=eng, subject="agent-x")
    plan = _plan(["invoke"])
    plan.get_step("s0").metadata["scope"] = PermissionScope.CAPABILITY_INVOKE
    plan.get_step("s0").metadata["resource"] = "capability:math"

    def handler(step, ctx):
        return "should-not-run"

    rep = ex.execute(plan, handler)
    assert rep.status == ExecutionOutcome.FAILED
    assert rep.results["s0"].status == "FAILED"


def test_execute_cancel_between_steps():
    ex = Executor()
    plan = _plan(["a", "b", "c"])
    ev = threading.Event()

    def handler(step, ctx):
        if step.step_id == "s0":
            ev.set()
        return step.step_id

    rep = ex.execute(plan, handler, cancel_event=ev)
    assert rep.status == ExecutionOutcome.CANCELLED
    assert "s0" in rep.results
    assert "s1" not in rep.results


def test_execute_emits_events():
    bus = EventBus()
    started = []
    finished = []

    @bus.on(Executor.__module__ and object)  # placeholder; use explicit subscribe
    def _noop(e):
        pass

    from aios.runtime.execution import ExecutionStarted, ExecutionStepFinished

    @bus.on(ExecutionStarted)
    def on_start(e):
        started.append(e.execution_id)

    @bus.on(ExecutionStepFinished)
    def on_finish(e):
        finished.append(e.step_id)

    ex = Executor(event_bus=bus)
    plan = _plan(["a", "b"])
    ex.execute(plan, lambda s, c: s.step_id)
    assert len(started) == 1
    assert set(finished) == {"s0", "s1"}


def test_execute_requires_execution_plan():
    ex = Executor()
    with pytest.raises(Exception):
        ex.execute("not-a-plan", lambda s, c: None)
