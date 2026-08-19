"""Execution state checkpoint / snapshot service (TASK-005, M1).

Supports snapshot-and-resume: the executor records an :class:`ExecutionState`
after each step so a failed/interrupted run can be restored and continued.

State is plain, JSON-serializable data (no live objects) so it can be persisted
to an artifact in a later task. This module depends only on stdlib + kernel
primitives.

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


__all__ = ["StateError", "RunStatus", "ExecutionState", "StateStore"]


class StateError(Exception):
    """Raised on state store errors."""


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionState:
    """A serializable checkpoint of one execution run."""

    execution_id: str
    status: RunStatus = RunStatus.RUNNING
    step_status: Dict[str, str] = field(default_factory=dict)
    cursor: int = 0  # index of the next step to run
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "step_status": dict(self.step_status),
            "cursor": self.cursor,
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
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            metadata=dict(data.get("metadata", {})),
        )

    def snapshot(self) -> "ExecutionState":
        return ExecutionState.from_dict(self.to_dict())


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
