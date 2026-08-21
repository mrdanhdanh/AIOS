"""Worker Registry — health-aware registry for Worker Plane (TASK-013).

Thread-safe, deterministic, fail-closed. Stores WorkerContract + health.

Layering: ``worker`` layer — stdlib + ``aios.core`` + ``aios.capability`` only.
Never imports ``runtime``/``orchestrator``/``agent``/``tool``.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Dict, List, Optional

from .contract import WorkerContract, WorkerError
from .lifecycle import WorkerHealth, WorkerLifecycle, WorkerStatus

__all__ = ["WorkerRegistry", "WorkerRegistryError", "RegisteredWorker"]


class WorkerRegistryError(Exception):
    pass


@dataclass
class RegisteredWorker:
    contract: WorkerContract
    health: WorkerHealth = WorkerHealth.REGISTERED
    status: WorkerStatus = WorkerStatus.REGISTERED

    def to_dict(self) -> dict:
        return {
            "contract": self.contract.to_dict(),
            "health": self.health.value,
            "status": self.status.value,
        }


class WorkerRegistry:
    """Thread-safe registry of WorkerContract + health/status."""

    def __init__(self, lifecycle: Optional[WorkerLifecycle] = None) -> None:
        self._lock = threading.RLock()
        self._workers: Dict[str, RegisteredWorker] = {}
        self._lifecycle = lifecycle or WorkerLifecycle()

    # -- CRUD ------------------------------------------------------------

    def register(self, contract: WorkerContract) -> RegisteredWorker:
        if not isinstance(contract, WorkerContract):
            raise WorkerRegistryError("contract must be WorkerContract")
        contract.validate()
        wid = contract.worker_id
        with self._lock:
            if wid in self._workers:
                raise WorkerRegistryError(f"worker already registered: {wid!r}")
            # Register in lifecycle as well
            try:
                self._lifecycle.register(wid)
            except Exception:
                # If already in lifecycle, ignore
                pass
            rw = RegisteredWorker(contract=contract, health=WorkerHealth.REGISTERED, status=WorkerStatus.REGISTERED)
            self._workers[wid] = rw
            return rw

    def get(self, worker_id: str) -> RegisteredWorker:
        with self._lock:
            if worker_id not in self._workers:
                raise WorkerRegistryError(f"unknown worker: {worker_id!r}")
            return self._workers[worker_id]

    def get_contract(self, worker_id: str) -> WorkerContract:
        return self.get(worker_id).contract

    def list(self) -> List[RegisteredWorker]:
        with self._lock:
            return sorted(self._workers.values(), key=lambda w: w.contract.worker_id)

    def list_contracts(self) -> List[WorkerContract]:
        return [rw.contract for rw in self.list()]

    def list_by_type(self, worker_type: str) -> List[RegisteredWorker]:
        with self._lock:
            return [rw for rw in self._workers.values() if rw.contract.worker_type.value == worker_type]

    def list_by_health(self, health: WorkerHealth | str) -> List[RegisteredWorker]:
        if isinstance(health, str):
            try:
                health = WorkerHealth(health)
            except ValueError as exc:
                raise WorkerRegistryError(f"invalid health {health!r}") from exc
        with self._lock:
            return [rw for rw in self._workers.values() if rw.health == health]

    def remove(self, worker_id: str) -> None:
        with self._lock:
            if worker_id not in self._workers:
                raise WorkerRegistryError(f"unknown worker: {worker_id!r}")
            del self._workers[worker_id]
            try:
                self._lifecycle.remove(worker_id)
            except Exception:
                pass

    def __len__(self) -> int:
        with self._lock:
            return len(self._workers)

    def __contains__(self, worker_id: str) -> bool:
        with self._lock:
            return worker_id in self._workers

    # -- health ----------------------------------------------------------

    def set_health(self, worker_id: str, health: WorkerHealth | str) -> RegisteredWorker:
        if isinstance(health, str):
            try:
                health = WorkerHealth(health)
            except ValueError as exc:
                raise WorkerRegistryError(f"invalid health {health!r}") from exc
        with self._lock:
            if worker_id not in self._workers:
                raise WorkerRegistryError(f"unknown worker: {worker_id!r}")
            rw = self._workers[worker_id]
            rw.health = health
            # Also update lifecycle health
            try:
                self._lifecycle.set_health(worker_id, health)
            except Exception:
                pass
            return rw

    def get_health(self, worker_id: str) -> WorkerHealth:
        return self.get(worker_id).health

    def is_available(self, worker_id: str) -> bool:
        """Available if health is READY or REGISTERED (not BUSY/DEGRADED/UNAVAILABLE)."""
        h = self.get_health(worker_id)
        return h in (WorkerHealth.READY, WorkerHealth.REGISTERED)

    def available_workers(self) -> List[RegisteredWorker]:
        with self._lock:
            return [rw for rw in self._workers.values() if rw.health in (WorkerHealth.READY, WorkerHealth.REGISTERED)]

    # -- lifecycle delegation --------------------------------------------

    @property
    def lifecycle(self) -> WorkerLifecycle:
        return self._lifecycle

    def set_status(self, worker_id: str, status: WorkerStatus | str) -> RegisteredWorker:
        if isinstance(status, str):
            try:
                status = WorkerStatus(status)
            except ValueError as exc:
                raise WorkerRegistryError(f"invalid status {status!r}") from exc
        with self._lock:
            if worker_id not in self._workers:
                raise WorkerRegistryError(f"unknown worker: {worker_id!r}")
            rw = self._workers[worker_id]
            # Transition via lifecycle
            self._lifecycle.transition(worker_id, status)
            rw.status = status
            rw.health = self._lifecycle.current_health(worker_id)
            return rw

    def clear(self) -> None:
        with self._lock:
            self._workers.clear()
            self._lifecycle.clear()

    def to_dict(self) -> Dict[str, dict]:
        with self._lock:
            return {wid: rw.to_dict() for wid, rw in self._workers.items()}
