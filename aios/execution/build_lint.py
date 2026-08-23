"""Build / Lint Runner (TASK-140, M20).

Runs build/lint inside a sandbox (T136) using a workspace (T137) under a policy
(T138), producing results with provenance. Fail-closed: a policy violation BLOCKs
the run (T078). Build/lint only run inside a sandbox (T136/T040). Every result
carries a ``content_hash`` (T078) and provenance (T001 Rule 5). Deterministic:
same target + same env -> same result.

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


class BuildVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class LintVerdict(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class BuildResult:
    target: str
    verdict: BuildVerdict
    content_hash: str


@dataclass
class LintResult:
    target: str
    verdict: LintVerdict
    content_hash: str


@dataclass
class BuildLintRun:
    """Result of a build/lint run with full provenance (T140)."""

    execution_ref: str
    sandbox_ref: str
    workspace_ref: str
    policy_ref: str
    build_results: List[BuildResult] = field(default_factory=list)
    lint_results: List[LintResult] = field(default_factory=list)
    evidence_ref: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")

    def content_hash(self) -> str:
        parts = [f"B:{r.target}:{r.verdict.value}:{r.content_hash}" for r in self.build_results]
        parts += [f"L:{r.target}:{r.verdict.value}:{r.content_hash}" for r in self.lint_results]
        return _hash("|".join(parts))


class BuildLintRunner:
    """Runs build/lint in a sandbox under policy (T140)."""

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
        command: str = "build",
        args: tuple = (),
    ) -> BuildLintRun:
        # Sandbox-only (T136/T040)
        if not self._sandbox.is_usable(sandbox_id):
            raise ExecutionError("Execution must run inside a usable sandbox (T136/T040).")
        # Policy enforce (T138)
        decision = self._policy.evaluate(policy_id, command)
        if decision.decision == Decision.DENY:
            raise ExecutionError(f"Policy denied build/lint: {decision.reason} (T078).")
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
        build_verdict = BuildVerdict.PASS if resp.exit_code == 0 else BuildVerdict.FAIL
        lint_verdict = LintVerdict.PASS if resp.exit_code == 0 else LintVerdict.FAIL
        return BuildLintRun(
            execution_ref=execution_id,
            sandbox_ref=sandbox_id,
            workspace_ref=workspace_id,
            policy_ref=policy_id,
            build_results=[
                BuildResult(target=command, verdict=build_verdict, content_hash=resp.stdout_hash or _hash(command))
            ],
            lint_results=[
                LintResult(
                    target=command,
                    verdict=lint_verdict,
                    content_hash=resp.stderr_hash or _hash(command + ":lint"),
                )
            ],
        )
