"""Tests for the security + replay harness (T143)."""

import pytest

from aios.execution import (
    ExecutionContract,
    ExecutionPolicy,
    ExecutionResponse,
    ExecutionStatus,
    PolicyEngine,
    ResourceLimit,
    SandboxManager,
    SecurityReplayHarness,
)
from aios.execution._common import ExecutionError, _hash
from aios.execution.tests._fake import FakeBlockedDispatcher, FakeDispatcher


def _fixture():
    contract = ExecutionContract(execution_id="ex1", sandbox_ref="sb1", policy_ref="pol1")
    sandbox = SandboxManager()
    sb = sandbox.create("network", policy_ref="pol1", sandbox_id="sb1")
    sandbox.isolate(sb.sandbox_id)
    policy = PolicyEngine()
    policy.register(
        ExecutionPolicy(
            execution_ref="ex1",
            resource_limit=ResourceLimit(2, 200),
            network_egress=True,
            command_allowlist=("run",),
            policy_id="pol1",
        )
    )
    return contract, sandbox, policy


def test_secure_run_ok():
    contract, sandbox, policy = _fixture()
    h = SecurityReplayHarness(contract, sandbox, policy, FakeDispatcher())
    resp = h.secure_run("ex1", "sb1", "pol1", command="run")
    assert resp.status == ExecutionStatus.SUCCESS


def test_secure_run_outside_sandbox():
    contract, sandbox, policy = _fixture()
    h = SecurityReplayHarness(contract, sandbox, policy, FakeDispatcher())
    with pytest.raises(ExecutionError):
        h.secure_run("ex1", "sb-x", "pol1", command="run")


def test_secure_run_policy_denied():
    contract, sandbox, policy = _fixture()
    h = SecurityReplayHarness(contract, sandbox, policy, FakeDispatcher())
    with pytest.raises(ExecutionError):
        h.secure_run("ex1", "sb1", "pol1", command="rm")


def test_secure_run_dispatcher_blocked():
    contract, sandbox, policy = _fixture()
    h = SecurityReplayHarness(contract, sandbox, policy, FakeBlockedDispatcher())
    with pytest.raises(ExecutionError):
        h.secure_run("ex1", "sb1", "pol1", command="run")


def test_replay_deterministic():
    contract, sandbox, policy = _fixture()
    h = SecurityReplayHarness(contract, sandbox, policy, FakeDispatcher())
    orig = ExecutionResponse(request_id="r1", status=ExecutionStatus.SUCCESS, exit_code=0, stdout_hash=_hash("run"), evidence_ref="ev1")
    repl = ExecutionResponse(request_id="r1", status=ExecutionStatus.SUCCESS, exit_code=0, stdout_hash=_hash("run"), evidence_ref="ev1")
    run = h.replay(orig, repl)
    assert run.replay_deterministic is True
    assert run.content_hash()


def test_replay_mismatch_detected():
    contract, sandbox, policy = _fixture()
    h = SecurityReplayHarness(contract, sandbox, policy, FakeDispatcher())
    orig = ExecutionResponse(request_id="r1", status=ExecutionStatus.SUCCESS, exit_code=0, stdout_hash=_hash("run"))
    repl = ExecutionResponse(request_id="r1", status=ExecutionStatus.SUCCESS, exit_code=1, stdout_hash=_hash("other"))
    with pytest.raises(ExecutionError):
        h.replay(orig, repl)
