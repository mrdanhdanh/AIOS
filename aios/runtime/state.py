"""Execution state checkpoint / snapshot service (TASK-005, M1).

Supports snapshot-and-resume: the executor records an :class:`ExecutionState`
after each step so a failed/interrupted run can be restored and continued.

State is plain, JSON-serializable data (no live objects) so it can be persisted
to an artifact in a later task. This module depends only on stdlib + kernel
primitives.

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


__all__ = [
    "StateError",
    "RunStatus",
    "ExecutionStatus",
    "Checkpoint",
    "Snapshot",
    "ExecutionState",
    "StateStore",
    "VALID_TRANSITIONS",
]


class StateError(Exception):
    """Raised on state store errors."""


class RunStatus(Enum):
    """Execution lifecycle states per TASK-005 spec.

    Canonical spec names are UPPER_CASE; values are lower-case for
    backward compatibility with existing tests. ``COMPLETED`` and
    ``SUCCEEDED`` are distinct members with different values — both are
    accepted as terminal success. ``SUCCEEDED`` is the spec-preferred name.
    """

    CREATED = "created"
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    COMPLETED = "completed"  # backward-compat alias for SUCCEEDED
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# Backward-compat alias: spec uses ExecutionStatus, implementation uses RunStatus.
ExecutionStatus = RunStatus

# Valid transitions per spec (controlled, not arbitrary).
# CREATED → PENDING → READY → RUNNING → {SUCCEEDED|COMPLETED|FAILED|CANCELLED|TIMEOUT}
# FAILED may transition to retry via re-enqueue (handled at Execution level).
VALID_TRANSITIONS: Dict[RunStatus, set] = {
    RunStatus.CREATED: {RunStatus.PENDING, RunStatus.CANCELLED},
    RunStatus.PENDING: {RunStatus.READY, RunStatus.CANCELLED, RunStatus.FAILED},
    RunStatus.READY: {RunStatus.RUNNING, RunStatus.CANCELLED, RunStatus.FAILED},
    RunStatus.RUNNING: {
        RunStatus.SUCCEEDED,
        RunStatus.COMPLETED,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
        RunStatus.TIMEOUT,
    },
    RunStatus.SUCCEEDED: set(),
    RunStatus.COMPLETED: set(),
    RunStatus.FAILED: set(),
    RunStatus.CANCELLED: set(),
    RunStatus.TIMEOUT: {RunStatus.FAILED, RunStatus.CANCELLED},
}


@dataclass
class ExecutionState:
    """A serializable checkpoint of one execution run.

    Extended for TASK-005 spec §2.6-2.8:
      - ``context_id`` and ``artifact_refs`` captured per checkpoint.
      - ``pending_nodes`` / ``completed_nodes`` derived from ``step_status``.
      - ``transition()`` enforces ``VALID_TRANSITIONS``.
      - ``to_checkpoint()`` materialises a spec-compliant :class:`Checkpoint`.
    """

    execution_id: str
    status: RunStatus = RunStatus.RUNNING
    step_status: Dict[str, str] = field(default_factory=dict)
    cursor: int = 0  # index of the next step to run
    context_id: Optional[str] = None
    artifact_refs: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def set_step(self, step_id: str, status: str) -> None:
        self.step_status[step_id] = status
        self.touch()

    def transition(self, target: RunStatus) -> None:
        """Controlled transition; raises :class:`StateError` on invalid move."""
        allowed = VALID_TRANSITIONS.get(self.status, set())
        # Allow idempotent (same status) and backward-compat: COMPLETED <-> SUCCEEDED
        if target == self.status:
            return
        if target in (RunStatus.COMPLETED, RunStatus.SUCCEEDED) and self.status in (
            RunStatus.COMPLETED,
            RunStatus.SUCCEEDED,
        ):
            self.status = target
            self.touch()
            return
        if target not in allowed:
            raise StateError(
                f"Invalid transition {self.status.value!r} → {target.value!r}"
            )
        self.status = target
        self.touch()

    @property
    def completed_nodes(self) -> List[str]:
        return [k for k, v in self.step_status.items() if v == "COMPLETED"]

    @property
    def pending_nodes(self) -> List[str]:
        return [k for k, v in self.step_status.items() if v != "COMPLETED"]

    def to_checkpoint(self, checkpoint_id: Optional[str] = None) -> "Checkpoint":
        """Materialise a spec §2.7 Checkpoint at the current boundary."""
        return Checkpoint(
            checkpoint_id=checkpoint_id or f"chk-{uuid.uuid4().hex[:12]}",
            execution_id=self.execution_id,
            status=self.status,
            context_id=self.context_id,
            step_status=dict(self.step_status),
            completed_nodes=list(self.completed_nodes),
            pending_nodes=list(self.pending_nodes),
            artifact_refs=dict(self.artifact_refs),
            cursor=self.cursor,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "step_status": dict(self.step_status),
            "cursor": self.cursor,
            "context_id": self.context_id,
            "artifact_refs": dict(self.artifact_refs),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionState":
        return cls(
            execution_id=data["execution_id"],
            status=RunStatus(data["status"]),
            step_status=dict(data.get("step_status", {})),
            cursor=int(data.get("cursor", 0)),
            context_id=data.get("context_id"),
            artifact_refs=dict(data.get("artifact_refs", {})),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            metadata=dict(data.get("metadata", {})),
        )

    def snapshot(self) -> "ExecutionState":
        return ExecutionState.from_dict(self.to_dict())


# --------------------------------------------------------------------------- #
# Checkpoint / Snapshot — spec §2.7-2.8
# --------------------------------------------------------------------------- #

@dataclass
class Checkpoint:
    """Boundary checkpoint after a node completes (spec §2.7).

    Stores an *immutable reference* (hash) to execution state, context,
    completed/pending nodes, artifact references and metadata — not a deep
    copy of artifacts themselves.
    """

    checkpoint_id: str
    execution_id: str
    status: RunStatus
    step_status: Dict[str, str] = field(default_factory=dict)
    completed_nodes: List[str] = field(default_factory=list)
    pending_nodes: List[str] = field(default_factory=list)
    artifact_refs: Dict[str, str] = field(default_factory=dict)
    context_id: Optional[str] = None
    cursor: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def content_hash(self) -> str:
        payload = json.dumps(
            {
                "checkpoint_id": self.checkpoint_id,
                "execution_id": self.execution_id,
                "status": self.status.value,
                "step_status": self.step_status,
                "artifact_refs": self.artifact_refs,
                "cursor": self.cursor,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "step_status": dict(self.step_status),
            "completed_nodes": list(self.completed_nodes),
            "pending_nodes": list(self.pending_nodes),
            "artifact_refs": dict(self.artifact_refs),
            "context_id": self.context_id,
            "cursor": self.cursor,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            execution_id=data["execution_id"],
            status=RunStatus(data["status"]),
            step_status=dict(data.get("step_status", {})),
            completed_nodes=list(data.get("completed_nodes", [])),
            pending_nodes=list(data.get("pending_nodes", [])),
            artifact_refs=dict(data.get("artifact_refs", {})),
            context_id=data.get("context_id"),
            cursor=int(data.get("cursor", 0)),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", ""),
        )


@dataclass
class Snapshot:
    """Immutable snapshot artifact for resume (spec §2.8).

    Wraps a :class:`Checkpoint` and adds integrity verification and
    version-compatibility fields required before resume.
    """

    snapshot_id: str
    checkpoint: Checkpoint
    workflow_version: str = "0.1.0"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    integrity_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.integrity_hash:
            self.integrity_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        payload = json.dumps(
            {
                "snapshot_id": self.snapshot_id,
                "checkpoint": self.checkpoint.to_dict(),
                "workflow_version": self.workflow_version,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        return self.integrity_hash == self._compute_hash()

    @property
    def is_valid(self) -> bool:
        return self.verify_integrity() and bool(self.checkpoint.checkpoint_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "checkpoint": self.checkpoint.to_dict(),
            "workflow_version": self.workflow_version,
            "created_at": self.created_at,
            "integrity_hash": self.integrity_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        chk = Checkpoint.from_dict(data["checkpoint"])
        snap = cls(
            snapshot_id=data["snapshot_id"],
            checkpoint=chk,
            workflow_version=data.get("workflow_version", "0.1.0"),
            created_at=data.get("created_at", ""),
            integrity_hash=data.get("integrity_hash", ""),
        )
        return snap

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint: Checkpoint,
        workflow_version: str = "0.1.0",
        snapshot_id: Optional[str] = None,
    ) -> "Snapshot":
        return cls(
            snapshot_id=snapshot_id or f"snap-{uuid.uuid4().hex[:12]}",
            checkpoint=checkpoint,
            workflow_version=workflow_version,
        )


class StateStore:
    """Thread-safe store of execution state checkpoints keyed by execution id."""

    def __init__(self) -> None:
        self._states: Dict[str, ExecutionState] = {}
        self._lock = threading.RLock()

    def save(self, state: ExecutionState) -> None:
        if not isinstance(state, ExecutionState):
            raise StateError("StateStore only holds ExecutionState")
        with self._lock:
            self._states[state.execution_id] = state.snapshot()

    def load(self, execution_id: str) -> Optional[ExecutionState]:
        with self._lock:
            st = self._states.get(execution_id)
            return st.snapshot() if st is not None else None

    def exists(self, execution_id: str) -> bool:
        with self._lock:
            return execution_id in self._states

    def delete(self, execution_id: str) -> None:
        with self._lock:
            self._states.pop(execution_id, None)

    def list_ids(self) -> List[str]:
        with self._lock:
            return sorted(self._states.keys())

    def __len__(self) -> int:
        with self._lock:
            return len(self._states)

    @staticmethod
    def new_execution_id() -> str:
        return f"exec-{uuid.uuid4().hex[:12]}"
