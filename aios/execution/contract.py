"""Execution Contract (TASK-135, M20).

Canonical execution contract shared by every M20 execution task. Defines the
standard request/response schema plus references to sandbox (T136), policy
(T113), artifact (T130) and evidence (T001). Pure, I/O-free, deterministic and
fail-closed: an invalid contract or request is rejected, never promoted to PASS.

Layering: ``execution`` is an ``unknown`` (infra) layer per the architecture
guard, so it may import stdlib + ``aios.core`` + ``aios.governance`` (unknown).
It must never import ``subprocess``/``os`` execution primitives, provider or
filesystem adapters directly (ARCH-001..004 spirit).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol, Tuple, runtime_checkable

from aios.execution._common import ExecutionError, _hash


class ExecutionStatus(str, Enum):
    """Standard execution outcome states (T135)."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ExecutionRequest:
    """Standard execution request schema (T135)."""

    request_id: str
    command: str
    args: Tuple[str, ...] = field(default_factory=tuple)
    env: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    cwd: Optional[str] = None
    sandbox_ref: Optional[str] = None
    policy_ref: Optional[str] = None
    artifact_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ExecutionError("request_id required (T001 Rule 1).")
        if not self.command:
            raise ExecutionError("command required.")


@dataclass(frozen=True)
class ExecutionResponse:
    """Standard execution response schema (T135)."""

    request_id: str
    status: ExecutionStatus
    exit_code: int = 0
    stdout_hash: str = ""
    stderr_hash: str = ""
    artifact_ref: Optional[str] = None
    evidence_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ExecutionError("request_id required.")
        if not isinstance(self.status, ExecutionStatus):
            raise ExecutionError("status must be ExecutionStatus.")


@runtime_checkable
class CapabilityDispatcher(Protocol):
    """Injected capability that actually performs an execution (T135/ARCH-004).

    The runner never executes directly; it dispatches through this protocol so
    the execution substrate stays behind a capability boundary.
    """

    def dispatch(self, request: ExecutionRequest) -> ExecutionResponse:
        """Execute ``request`` and return a standardized response."""
        ...


@dataclass
class ExecutionContract:
    """Canonical execution contract (T135).

    Every M20 execution task implements this contract. It carries references to
    the sandbox (T136), policy (T113), artifact (T130) and evidence (T001) used
    by the execution. Fail-closed: a contract missing its immutable execution_id
    or a request/response that violates the schema is rejected.
    """

    execution_id: str
    request_schema: str = "ExecutionRequest"
    response_schema: str = "ExecutionResponse"
    sandbox_ref: Optional[str] = None
    policy_ref: Optional[str] = None
    artifact_ref: Optional[str] = None
    evidence_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.execution_id:
            raise ExecutionError("execution_id required (T001 Rule 1, immutable).")

    # -- validation (fail-closed) -------------------------------------- #
    def validate_request(self, req: ExecutionRequest) -> bool:
        """Return True only when the request satisfies the contract.

        Fail-closed: a request without a policy reference (T113 boundary) or a
        sandbox reference (T136 boundary) is rejected.
        """
        if not isinstance(req, ExecutionRequest):
            return False
        if self.policy_ref is None and req.policy_ref is None:
            return False
        if self.sandbox_ref is None and req.sandbox_ref is None:
            return False
        return True

    def validate_response(self, resp: ExecutionResponse) -> bool:
        """Return True only when the response satisfies the contract."""
        if not isinstance(resp, ExecutionResponse):
            return False
        if resp.status == ExecutionStatus.BLOCKED and self.policy_ref is None:
            # A BLOCKED response must be attributable to a policy decision.
            return False
        return True

    # -- provenance --------------------------------------------------- #
    def content_hash(self) -> str:
        payload = (
            f"{self.execution_id}|{self.request_schema}|{self.response_schema}|"
            f"{self.sandbox_ref}|{self.policy_ref}|{self.artifact_ref}|{self.evidence_ref}"
        )
        return _hash(payload)

    def provenance(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "sandbox_ref": self.sandbox_ref,
            "policy_ref": self.policy_ref,
            "artifact_ref": self.artifact_ref,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash(),
        }
