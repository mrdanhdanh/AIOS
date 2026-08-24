"""Tests for the real tool execution handler (TASK-222)."""

from __future__ import annotations

import sys

import pytest

from aios.core.planner import ExecutionPlan, Step
from aios.runtime.execution import Executor
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyEngine
from aios.runtime.process import (
    RealToolHandler,
    SCOPE_MAP,
    _is_denied_command,
)
from aios.governance.evidence.store import EvidenceStore, record_execution_evidence


def _granted_broker() -> PermissionBroker:
    b = PermissionBroker()
    b.grant("runtime", Permission(PermissionScope.EXECUTE, "*"))
    return b


def _step(command: str, timeout: float = 10.0) -> Step:
    return Step(
        step_id="s1",
        action=command,
        metadata={
            "command": command,
            "tool_type": "shell",
            "scope": PermissionScope.EXECUTE,
            "resource": "s1",
            "timeout": timeout,
        },
    )


def test_scope_map():
    assert SCOPE_MAP["process.execute"] is PermissionScope.EXECUTE
    assert SCOPE_MAP["tool:invoke"] is PermissionScope.TOOL_INVOKE
    assert SCOPE_MAP["filesystem.write"] is PermissionScope.WRITE
    assert SCOPE_MAP["filesystem.read"] is PermissionScope.READ


def test_denylist_detection():
    assert _is_denied_command("rm -rf /")
    assert not _is_denied_command("echo hello")


def test_real_handler_runs_echo():
    h = RealToolHandler(_granted_broker(), subject="runtime")
    out = h(_step("echo hello-from-aios"), None)
    assert "hello-from-aios" in out


def test_real_handler_denied_without_grant():
    h = RealToolHandler(PermissionBroker(), subject="runtime")
    with pytest.raises(PermissionError):
        h(_step("echo hi"), None)


def test_real_handler_denylist_blocks():
    h = RealToolHandler(_granted_broker(), subject="runtime")
    with pytest.raises(PermissionError):
        h(_step("rm -rf /"), None)


def test_real_handler_timeout_kills_process():
    broker = _granted_broker()
    policy = PolicyEngine(broker=broker)
    ex = Executor(policy=policy)
    h = RealToolHandler(broker, subject="runtime")
    plan = ExecutionPlan(plan_id="p-timeout")
    plan.add_step(
        _step(f'{sys.executable} -c "import time; time.sleep(10)"', timeout=1.0)
    )
    report = ex.execute(plan, h, timeout=1.0)
    assert report.results["s1"].status == "TIMEOUT"


def test_real_handler_via_executor_policy_gate():
    broker = _granted_broker()
    policy = PolicyEngine(broker=broker)
    ex = Executor(policy=policy)
    h = RealToolHandler(broker, subject="runtime")
    plan = ExecutionPlan(plan_id="p1")
    plan.add_step(_step("echo via-executor"))
    report = ex.execute(plan, h, timeout=10.0)
    assert report.is_success
    assert "via-executor" in str(report.results["s1"].output)


def test_record_execution_evidence_chain():
    broker = _granted_broker()
    policy = PolicyEngine(broker=broker)
    ex = Executor(policy=policy)
    h = RealToolHandler(broker, subject="runtime")
    plan = ExecutionPlan(plan_id="p1")
    plan.add_step(_step("echo evidence-chain"))
    report = ex.execute(plan, h, timeout=10.0)
    store = EvidenceStore()
    ids = record_execution_evidence(store, "wf", "0.1.0", plan, report, "plan.yaml")
    assert ids
    chain = store.get_provenance_chain(ids[0])
    assert chain.complete is True
