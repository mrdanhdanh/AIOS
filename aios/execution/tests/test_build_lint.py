"""Tests for the build/lint runner (T140)."""

import pytest

from aios.execution import (
    BuildVerdict,
    ExecutionContract,
    ExecutionPolicy,
    LintVerdict,
    PolicyEngine,
    ResourceLimit,
    SandboxManager,
    WorkspaceManager,
    BuildLintRunner,
)
from aios.execution._common import ExecutionError
from aios.execution.tests._fake import FakeBlockedDispatcher, FakeDispatcher


def _fixture():
    contract = ExecutionContract(execution_id="ex1", sandbox_ref="sb1", policy_ref="pol1")
    sandbox = SandboxManager()
    sb = sandbox.create("fs", policy_ref="pol1", sandbox_id="sb1")
    sandbox.isolate(sb.sandbox_id)
    workspace = WorkspaceManager()
    workspace.create(policy_ref="pol1", workspace_id="ws1")
    policy = PolicyEngine()
    policy.register(
        ExecutionPolicy(
            execution_ref="ex1",
            resource_limit=ResourceLimit(2, 200),
            network_egress=True,
            command_allowlist=("build", "lint"),
            policy_id="pol1",
        )
    )
    return contract, sandbox, workspace, policy


def test_build_pass():
    contract, sandbox, workspace, policy = _fixture()
    runner = BuildLintRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    run = runner.run("ex1", "sb1", "ws1", "pol1", command="build")
    assert run.build_results[0].verdict == BuildVerdict.PASS
    assert run.lint_results[0].verdict == LintVerdict.PASS


def test_outside_sandbox_blocked():
    contract, sandbox, workspace, policy = _fixture()
    runner = BuildLintRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    with pytest.raises(ExecutionError):
        runner.run("ex1", "sb-x", "ws1", "pol1", command="build")


def test_policy_denied():
    contract, sandbox, workspace, policy = _fixture()
    runner = BuildLintRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    with pytest.raises(ExecutionError):
        runner.run("ex1", "sb1", "ws1", "pol1", command="rm")


def test_dispatcher_blocked():
    contract, sandbox, workspace, policy = _fixture()
    runner = BuildLintRunner(contract, sandbox, workspace, policy, FakeBlockedDispatcher())
    with pytest.raises(ExecutionError):
        runner.run("ex1", "sb1", "ws1", "pol1", command="build")


def test_content_hash():
    contract, sandbox, workspace, policy = _fixture()
    runner = BuildLintRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    run = runner.run("ex1", "sb1", "ws1", "pol1", command="build")
    assert run.content_hash()


def test_deterministic():
    contract, sandbox, workspace, policy = _fixture()
    r1 = BuildLintRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    r2 = BuildLintRunner(contract, sandbox, workspace, policy, FakeDispatcher())
    a = r1.run("ex1", "sb1", "ws1", "pol1", command="build")
    b = r2.run("ex1", "sb1", "ws1", "pol1", command="build")
    assert a.content_hash() == b.content_hash()
