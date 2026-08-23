"""Tests for the test runner (T139)."""

import pytest

from aios.execution import (
    ExecutionContract,
    ExecutionPolicy,
    PolicyEngine,
    ResourceLimit,
    SandboxManager,
    TestRunner,
    WorkspaceManager,
)
from aios.execution._common import ExecutionError
from aios.execution.tests._fake import FakeBlockedDispatcher, FakeDispatcher


def _fixture():
    contract = ExecutionContract(execution_id="ex1", sandbox_ref="sb1", policy_ref="pol1")
    sandbox = SandboxManager()
    sb = sandbox.create("process", policy_ref="pol1", sandbox_id="sb1")
    sandbox.isolate(sb.sandbox_id)
    workspace = WorkspaceManager()
    ws = workspace.create(policy_ref="pol1", workspace_id="ws1")
    policy = PolicyEngine()
    policy.register(
        ExecutionPolicy(
            execution_ref="ex1",
            resource_limit=ResourceLimit(2, 200),
            network_egress=True,
            command_allowlist=("pytest",),
            policy_id="pol1",
        )
    )
    return contract, sandbox, workspace, policy


def test_run_pass_in_sandbox():
    contract, sandbox, workspace, policy = _fixture()
    runner = TestRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    run = runner.run("ex1", "sb1", "ws1", "pol1", command="pytest")
    assert run.results[0].verdict.value == "pass"
    assert run.sandbox_ref == "sb1"


def test_run_outside_sandbox_blocked():
    contract, sandbox, workspace, policy = _fixture()
    runner = TestRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    with pytest.raises(ExecutionError):
        runner.run("ex1", "sb-unknown", "ws1", "pol1", command="pytest")


def test_run_policy_denied():
    contract, sandbox, workspace, policy = _fixture()
    runner = TestRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    with pytest.raises(ExecutionError):
        runner.run("ex1", "sb1", "ws1", "pol1", command="rm")


def test_run_dispatcher_blocked():
    contract, sandbox, workspace, policy = _fixture()
    runner = TestRunner(contract, sandbox, workspace, policy, FakeBlockedDispatcher())
    with pytest.raises(ExecutionError):
        runner.run("ex1", "sb1", "ws1", "pol1", command="pytest")


def test_result_has_hash():
    contract, sandbox, workspace, policy = _fixture()
    runner = TestRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    run = runner.run("ex1", "sb1", "ws1", "pol1", command="pytest")
    assert run.results[0].content_hash
    assert run.content_hash()


def test_deterministic_same_env():
    contract, sandbox, workspace, policy = _fixture()
    r1 = TestRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    r2 = TestRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    a = r1.run("ex1", "sb1", "ws1", "pol1", command="pytest")
    b = r2.run("ex1", "sb1", "ws1", "pol1", command="pytest")
    assert a.content_hash() == b.content_hash()
