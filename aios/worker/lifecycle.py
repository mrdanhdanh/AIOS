"""Worker lifecycle — state machine for Worker Plane (TASK-013).

Worker lifecycle is distinct from Task lifecycle. A worker can remain READY
after its task fails.

States:
    REGISTERED -> READY -> ASSIGNED -> RUNNING -> COMPLETING -> COMPLETED
    RUNNING -> FAILED -> RECOVERING -> READY | FAILED
    Any non-terminal -> CANCELLED
Terminal: COMPLETED, FAILED (after RECOVERING), CANCELLED

Health (separate dimension):
    REGISTERED, READY, BUSY, DEGRADED, UNAVAILABLE

Layering: ``worker`` layer — stdlib + ``aios.core`` only.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set

__all__ = [
    "WorkerStatus",
    "WorkerHealth",
    "WorkerLifecycle",
    "WorkerLifecycleError",
]


class WorkerLifecycleError(Exception):
    pass


class WorkerStatus(str, Enum):
    REGISTERED = "REGISTERED"
    READY = "READY"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    COMPLETING = "COMPLETING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
    CANCELLED = "CANCELLED"


class WorkerHealth(str, Enum):
    REGISTERED = "REGISTERED"
    READY = "READY"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


# Valid transitions per T013 §7
_VALID_TRANSITIONS: Dict[WorkerStatus, Set[WorkerStatus]] = {
    WorkerStatus.REGISTERED: {WorkerStatus.READY, WorkerStatus.CANCELLED},
    WorkerStatus.READY: {WorkerStatus.ASSIGNED, WorkerStatus.CANCELLED},
    WorkerStatus.ASSIGNED: {WorkerStatus.RUNNING, WorkerStatus.CANCELLED},
    WorkerStatus.RUNNING: {WorkerStatus.COMPLETING, WorkerStatus.FAILED, WorkerStatus.CANCELLED},
    WorkerStatus.COMPLETING: {WorkerStatus.COMPLETED, WorkerStatus.FAILED, WorkerStatus.CANCELLED},
    WorkerStatus.COMPLETED: set(),  # terminal
    WorkerStatus.FAILED: {WorkerStatus.RECOVERING, WorkerStatus.CANCELLED},
    WorkerStatus.RECOVERING: {WorkerStatus.READY, WorkerStatus.FAILED, WorkerStatus.CANCELLED},
    WorkerStatus.CANCELLED: set(),  # terminal
}

_TERMINAL: Set[WorkerStatus] = {
    WorkerStatus.COMPLETED,
    WorkerStatus.CANCELLED,
}

# FAILED is terminal only if not going to RECOVERING; but we treat it as
# semi-terminal — it can still go to RECOVERING. For is_terminal check,
# we consider COMPLETED and CANCELLED as hard terminal, FAILED as soft.
_HARD_TERMINAL: Set[WorkerStatus] = {WorkerStatus.COMPLETED, WorkerStatus.CANCELLED}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkerState:
    worker_id: str
    status: WorkerStatus = WorkerStatus.REGISTERED
    health: WorkerHealth = WorkerHealth.REGISTERED
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, object] = None  # type: ignore

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = WorkerStatus(self.status)
            except ValueError as exc:
                raise WorkerLifecycleError(f"invalid status {self.status!r}") from exc
        if isinstance(self.health, str):
            try:
                self.health = WorkerHealth(self.health)
            except ValueError as exc:
                raise WorkerLifecycleError(f"invalid health {self.health!r}") from exc
        if not self.created_at:
            self.created_at = _now()
        if not self.updated_at:
            self.updated_at = _now()
        if self.metadata is None:
            self.metadata = {}


class WorkerLifecycle:
    """Thread-safe state machine for worker lifecycle."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._states: Dict[str, WorkerState] = {}

    # -- registration ----------------------------------------------------

    def register(self, worker_id: str, metadata: Optional[Dict[str, object]] = None) -> WorkerState:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise WorkerLifecycleError("worker_id must be non-empty string")
        with self._lock:
            if worker_id in self._states:
                raise WorkerLifecycleError(f"worker already registered: {worker_id!r}")
            state = WorkerState(
                worker_id=worker_id,
                status=WorkerStatus.REGISTERED,
                health=WorkerHealth.REGISTERED,
                metadata=dict(metadata or {}),
            )
            self._states[worker_id] = state
            return state

    def get(self, worker_id: str) -> WorkerState:
        with self._lock:
            if worker_id not in self._states:
                raise WorkerLifecycleError(f"unknown worker: {worker_id!r}")
            return self._states[worker_id]

    def current_status(self, worker_id: str) -> WorkerStatus:
        return self.get(worker_id).status

    def current_health(self, worker_id: str) -> WorkerHealth:
        return self.get(worker_id).health

    def list_all(self) -> List[WorkerState]:
        with self._lock:
            return list(self._states.values())

    def is_terminal(self, worker_id: str) -> bool:
        status = self.current_status(worker_id)
        return status in _HARD_TERMINAL

    def is_failed(self, worker_id: str) -> bool:
        return self.current_status(worker_id) == WorkerStatus.FAILED

    # -- transitions -----------------------------------------------------

    def can_transition(self, worker_id: str, target: WorkerStatus) -> bool:
        if isinstance(target, str):
            try:
                target = WorkerStatus(target)
            except ValueError:
                return False
        with self._lock:
            state = self._states.get(worker_id)
            if state is None:
                return False
            if target == state.status:
                return True
            allowed = _VALID_TRANSITIONS.get(state.status, set())
            return target in allowed

    def transition(self, worker_id: str, target: WorkerStatus | str) -> WorkerState:
        if isinstance(target, str):
            try:
                target = WorkerStatus(target)
            except ValueError as exc:
                raise WorkerLifecycleError(f"invalid target status {target!r}") from exc
        with self._lock:
            if worker_id not in self._states:
                raise WorkerLifecycleError(f"unknown worker: {worker_id!r}")
            state = self._states[worker_id]
            if target == state.status:
                return state
            allowed = _VALID_TRANSITIONS.get(state.status, set())
            if target not in allowed:
                raise WorkerLifecycleError(
                    f"invalid transition {state.status.value} -> {target.value} for worker {worker_id!r}"
                )
            state.status = target
            state.updated_at = _now()
            # Update health to reflect status
            state.health = self._health_for_status(target)
            return state

    def _health_for_status(self, status: WorkerStatus) -> WorkerHealth:
        mapping = {
            WorkerStatus.REGISTERED: WorkerHealth.REGISTERED,
            WorkerStatus.READY: WorkerHealth.READY,
            WorkerStatus.ASSIGNED: WorkerHealth.BUSY,
            WorkerStatus.RUNNING: WorkerHealth.BUSY,
            WorkerStatus.COMPLETING: WorkerHealth.BUSY,
            WorkerStatus.COMPLETED: WorkerHealth.READY,
            WorkerStatus.FAILED: WorkerHealth.DEGRADED,
            WorkerStatus.RECOVERING: WorkerHealth.DEGRADED,
            WorkerStatus.CANCELLED: WorkerHealth.UNAVAILABLE,
        }
        return mapping.get(status, WorkerHealth.READY)

    # -- convenience transitions -----------------------------------------

    def mark_ready(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.READY)

    def assign(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.ASSIGNED)

    def start(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.RUNNING)

    def completing(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.COMPLETING)

    def complete(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.COMPLETED)

    def fail(self, worker_id: str) -> WorkerState:
        # Can fail from RUNNING or COMPLETING
        current = self.current_status(worker_id)
        if current in (WorkerStatus.RUNNING, WorkerStatus.COMPLETING):
            return self.transition(worker_id, WorkerStatus.FAILED)
        # Also allow direct fail from ASSIGNED/RUNNING etc via transition
        return self.transition(worker_id, WorkerStatus.FAILED)

    def recovering(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.RECOVERING)

    def recover_to_ready(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.READY)

    def recover_to_failed(self, worker_id: str) -> WorkerState:
        # RECOVERING -> FAILED
        return self.transition(worker_id, WorkerStatus.FAILED)

    def cancel(self, worker_id: str) -> WorkerState:
        return self.transition(worker_id, WorkerStatus.CANCELLED)

    def set_health(self, worker_id: str, health: WorkerHealth | str) -> WorkerState:
        if isinstance(health, str):
            try:
                health = WorkerHealth(health)
            except ValueError as exc:
                raise WorkerLifecycleError(f"invalid health {health!r}") from exc
        with self._lock:
            if worker_id not in self._states:
                raise WorkerLifecycleError(f"unknown worker: {worker_id!r}")
            state = self._states[worker_id]
            state.health = health
            state.updated_at = _now()
            return state

    def remove(self, worker_id: str) -> None:
        with self._lock:
            if worker_id not in self._states:
                raise WorkerLifecycleError(f"unknown worker: {worker_id!r}")
            del self._states[worker_id]

    def clear(self) -> None:
        with self._lock:
            self._states.clear()

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        with self._lock:
            return {
                wid: {
                    "status": st.status.value,
                    "health": st.health.value,
                    "created_at": st.created_at,
                    "updated_at": st.updated_at,
                }
                for wid, st in self._states.items()
            }
