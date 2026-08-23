"""Security + Replay Harness (TASK-143, M20).

Runs an execution (T135) inside a sandbox (T136) under policy (T138) and replays
it deterministically from evidence (T141/T142). Fail-closed: a replay mismatch is
detected (T078). Every replay carries provenance (T001 Rule 5). Deterministic:
same evidence -> same output.

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

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


@dataclass
class ReplayRun:
    """Record of a deterministic replay (T143)."""

    execution_ref: str
    sandbox_ref: str
    policy_ref: str
    evidence_ref: str
    replay_deterministic: bool
    original_output_hash: str = ""
    replay_output_hash: str = ""
    evidence_ref2: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")

    def content_hash(self) -> str:
        return _hash(
            f"{self.execution_ref}|{self.sandbox_ref}|{self.policy_ref}|"
            f"{self.replay_deterministic}|{self.original_output_hash}|{self.replay_output_hash}"
        )


class SecurityReplayHarness:
    """Secure run + deterministic replay harness (T143)."""

    def __init__(
        self,
        contract: ExecutionContract,
        sandbox: SandboxManager,
        policy_engine: PolicyEngine,
        dispatcher: CapabilityDispatcher,
    ) -> None:
        self._contract = contract
        self._sandbox = sandbox
        self._policy = policy_engine
        self._dispatcher = dispatcher

    def secure_run(
        self,
        execution_id: str,
        sandbox_id: str,
        policy_id: str,
        command: str = "run",
        args: tuple = (),
    ) -> ExecutionResponse:
        # Sandbox-only (T136/T040)
        if not self._sandbox.is_usable(sandbox_id):
            raise ExecutionError("Secure run requires a usable sandbox (T136/T040).")
        # Policy enforce (T138)
        decision = self._policy.evaluate(policy_id, command)
        if decision.decision == Decision.DENY:
            raise ExecutionError(f"Policy denied secure run: {decision.reason} (T138).")
        req = ExecutionRequest(
            request_id=f"req-{uuid.uuid4().hex[:12]}",
            command=command,
            args=tuple(args),
            sandbox_ref=sandbox_id,
            policy_ref=policy_id,
        )
        if not self._contract.validate_request(req):
            raise ExecutionError("Request failed contract validation (T135).")
        resp = self._dispatcher.dispatch(req)
        if resp.status == ExecutionStatus.BLOCKED:
            raise ExecutionError("Dispatcher blocked execution (T078).")
        return resp

    def replay(
        self,
        original: ExecutionResponse,
        replayed: ExecutionResponse,
        sandbox_ref: str = "",
        policy_ref: str = "",
    ) -> ReplayRun:
        """Replay and assert determinism (T030/T078).

        Fail-closed: a mismatch between the original and replayed output is
        detected by raising (T078).
        """
        original_hash = original.stdout_hash or _hash(original.request_id)
        replay_hash = replayed.stdout_hash or _hash(replayed.request_id)
        deterministic = (
            original_hash == replay_hash and original.exit_code == replayed.exit_code
        )
        if not deterministic:
            raise ExecutionError("Replay mismatch detected (fail-closed, T078).")
        return ReplayRun(
            execution_ref=original.request_id,
            sandbox_ref=sandbox_ref,
            policy_ref=policy_ref,
            evidence_ref=original.evidence_ref or "",
            replay_deterministic=True,
            original_output_hash=original_hash,
            replay_output_hash=replay_hash,
        )
