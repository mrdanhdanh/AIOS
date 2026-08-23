"""Test Runner (TASK-139, M20).

Runs a test suite inside a sandbox (T136) using a workspace (T137) under a policy
(T138), producing results with provenance. Fail-closed: a policy violation BLOCKs
the run (T078). Tests only run inside a sandbox (T136/T040). Every result carries
a ``content_hash`` (T078) and provenance (T001 Rule 5). Deterministic: same
suite + same env -> same result.

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from aios.execution._common import ExecutionError, _hash
from aios.execution.contract import (
    CapabilityDispatcher,
    ExecutionContract,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatus,
)
from aios.execution.policy import Decision, PolicyEngine
from aios.execution.sandbox import SandboxManager
from aios.execution.workspace import WorkspaceManager


class TestVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass
class TestResult:
    """A single test outcome with integrity hash (T139)."""

    name: str
    verdict: TestVerdict
    content_hash: str

    def __post_init__(self) -> None:
        if not self.content_hash:
            raise ExecutionError("TestResult requires content_hash (T078).")


@dataclass
class TestRun:
    """Result of a test run with full provenance (T139)."""

    execution_ref: str
    sandbox_ref: str
    workspace_ref: str
    policy_ref: str
    results: List[TestResult] = field(default_factory=list)
    evidence_ref: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")

    def content_hash(self) -> str:
        parts = [f"{r.name}:{r.verdict.value}:{r.content_hash}" for r in self.results]
        return _hash("|".join(parts))


class TestRunner:
    """Runs test suites in a sandbox under policy (T139)."""

    def __init__(
        self,
        contract: ExecutionContract,
        sandbox: SandboxManager,
        workspace: WorkspaceManager,
        policy_engine: PolicyEngine,
        dispatcher: CapabilityDispatcher,
    ) -> None:
        self._contract = contract
        self._sandbox = sandbox
        self._workspace = workspace
        self._policy = policy_engine
        self._dispatcher = dispatcher

    def run(
        self,
        execution_id: str,
        sandbox_id: str,
        workspace_id: str,
        policy_id: str,
        command: str = "pytest",
        args: tuple = (),
    ) -> TestRun:
        # Sandbox-only (T136/T040)
        if not self._sandbox.is_usable(sandbox_id):
            raise ExecutionError("Execution must run inside a usable sandbox (T136/T040).")
        # Policy enforce (T138)
        decision = self._policy.evaluate(policy_id, command)
        if decision.decision == Decision.DENY:
            raise ExecutionError(f"Policy denied test run: {decision.reason} (T078).")
        # Build request via contract
        req = ExecutionRequest(
            request_id=f"req-{uuid.uuid4().hex[:12]}",
            command=command,
            args=tuple(args),
            sandbox_ref=sandbox_id,
            policy_ref=policy_id,
            artifact_ref=workspace_id,
        )
        if not self._contract.validate_request(req):
            raise ExecutionError("Request failed contract validation (T135).")
        resp = self._dispatcher.dispatch(req)
        if resp.status == ExecutionStatus.BLOCKED:
            raise ExecutionError("Dispatcher blocked execution (T078).")
        # Deterministic result from the (sandboxed) response.
        verdict = TestVerdict.PASS if resp.exit_code == 0 else TestVerdict.FAIL
        result = TestResult(
            name=command,
            verdict=verdict,
            content_hash=resp.stdout_hash or _hash(command),
        )
        return TestRun(
            execution_ref=execution_id,
            sandbox_ref=sandbox_id,
            workspace_ref=workspace_id,
            policy_ref=policy_id,
            results=[result],
        )
