"""Sandbox Manager (TASK-136, M20).

Manages sandbox lifecycle (create/destroy/isolate) so executions (T135) run
isolated without touching Core. ``sandbox_id`` is immutable (T001 Rule 1). Every
lifecycle event carries provenance (T001 Rule 5). Fail-closed: a sandbox that
cannot be isolated is rejected (T040/T078).

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from aios.execution._common import ExecutionError, _hash, _now


class IsolationLevel(str, Enum):
    """Isolation dimensions (T040)."""

    PROCESS = "process"
    FS = "fs"
    NETWORK = "network"


class SandboxStatus(str, Enum):
    """Sandbox lifecycle states (T136)."""

    CREATED = "created"
    ISOLATED = "isolated"
    DESTROYED = "destroyed"


@dataclass
class SandboxRecord:
    """Immutable-by-id sandbox record (T136)."""

    sandbox_id: str
    status: SandboxStatus
    isolation_level: IsolationLevel
    health: str  # healthy | unhealthy
    policy_ref: Optional[str] = None
    evidence_ref: Optional[str] = None
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.sandbox_id:
            raise ExecutionError("sandbox_id required (T001 Rule 1, immutable).")


class SandboxManager:
    """Manages sandbox lifecycle with fail-closed isolation (T136)."""

    def __init__(self) -> None:
        self._sandboxes: Dict[str, SandboxRecord] = {}

    def create(
        self,
        isolation_level: IsolationLevel,
        policy_ref: Optional[str] = None,
        sandbox_id: Optional[str] = None,
    ) -> SandboxRecord:
        sid = sandbox_id or f"sb-{uuid.uuid4().hex[:12]}"
        if sid in self._sandboxes:
            raise ExecutionError(f"Duplicate sandbox_id '{sid}' (T001 Rule 1).")
        rec = SandboxRecord(
            sandbox_id=sid,
            status=SandboxStatus.CREATED,
            isolation_level=isolation_level,
            health="healthy",
            policy_ref=policy_ref,
            evidence_ref=f"ev-{uuid.uuid4().hex[:12]}",
        )
        self._sandboxes[sid] = rec
        return rec

    def isolate(self, sandbox_id: str) -> SandboxRecord:
        rec = self._get(sandbox_id)
        # Fail-closed: cannot isolate without a policy boundary (T113/T040).
        if rec.policy_ref is None:
            raise ExecutionError("Cannot isolate sandbox without policy_ref (T113).")
        rec.status = SandboxStatus.ISOLATED
        rec.evidence_ref = f"ev-{uuid.uuid4().hex[:12]}"
        return rec

    def healthcheck(self, sandbox_id: str) -> bool:
        return self._get(sandbox_id).health == "healthy"

    def destroy(self, sandbox_id: str) -> SandboxRecord:
        rec = self._get(sandbox_id)
        rec.status = SandboxStatus.DESTROYED
        rec.evidence_ref = f"ev-{uuid.uuid4().hex[:12]}"
        return rec

    def is_usable(self, sandbox_id: str) -> bool:
        """An execution may only run in a healthy, isolated sandbox (T135/T040)."""
        rec = self._get(sandbox_id)
        return rec.status == SandboxStatus.ISOLATED and rec.health == "healthy"

    def get(self, sandbox_id: str) -> SandboxRecord:
        return self._get(sandbox_id)

    def _get(self, sandbox_id: str) -> SandboxRecord:
        if sandbox_id not in self._sandboxes:
            raise ExecutionError(f"Unknown sandbox '{sandbox_id}'.")
        return self._sandboxes[sandbox_id]

    def provenance(self, sandbox_id: str) -> dict:
        rec = self._get(sandbox_id)
        payload = (
            f"{rec.sandbox_id}|{rec.status.value}|"
            f"{rec.isolation_level.value}|{rec.health}|{rec.policy_ref}"
        )
        return {
            "sandbox_id": rec.sandbox_id,
            "status": rec.status.value,
            "isolation_level": rec.isolation_level.value,
            "health": rec.health,
            "policy_ref": rec.policy_ref,
            "evidence_ref": rec.evidence_ref,
            "content_hash": _hash(payload),
        }
