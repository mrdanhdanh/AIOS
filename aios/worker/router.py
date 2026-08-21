"""Worker Router — capability-based routing for Worker Plane (TASK-013).

Routes tasks to workers based on task_type, required_capabilities,
worker health, policy and availability. Deterministic, fail-closed.

Layering: ``worker`` layer — stdlib + ``aios.core`` + ``aios.capability`` only.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .contract import WorkerContract
from .lifecycle import WorkerHealth
from .registry import RegisteredWorker, WorkerRegistry, WorkerRegistryError

__all__ = ["WorkerRouter", "WorkerRouterError", "RoutingDecision", "RoutingRequest"]


class WorkerRouterError(Exception):
    pass


@dataclass
class RoutingRequest:
    """Request to route a task to a worker."""

    task_id: str
    task_type: str = "general"  # general | coding | diagnosis | system_diagnosis
    required_capabilities: List[str] = field(default_factory=list)
    preferred_worker_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise WorkerRouterError("task_id must be non-empty string")
        if not isinstance(self.task_type, str) or not self.task_type.strip():
            raise WorkerRouterError("task_type must be non-empty string")
        if not isinstance(self.required_capabilities, list):
            raise WorkerRouterError("required_capabilities must be a list")
        for c in self.required_capabilities:
            if not isinstance(c, str) or not c.strip():
                raise WorkerRouterError(f"capability {c!r} must be non-empty string")


@dataclass
class RoutingDecision:
    """Result of routing."""

    task_id: str
    worker_id: str
    worker_type: str
    reason: str
    is_fallback: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "worker_id": self.worker_id,
            "worker_type": self.worker_type,
            "reason": self.reason,
            "is_fallback": self.is_fallback,
            "metadata": dict(self.metadata),
        }


# Task type → preferred worker type mapping
_TASK_TYPE_TO_WORKER_TYPE: Dict[str, str] = {
    "general": "general",
    "research": "general",
    "summarize": "general",
    "transform": "general",
    "inspect": "general",
    "coordinate": "general",
    "coding": "coder",
    "code": "coder",
    "edit_code": "coder",
    "run_tests": "coder",
    "refactor": "coder",
    "diagnosis": "doctor",
    "diagnose": "doctor",
    "task_diagnosis": "doctor",
    "system_diagnosis": "system_doctor",
    "runtime_diagnosis": "system_doctor",
    "health_check": "system_doctor",
}


class WorkerRouter:
    """Routes tasks to workers based on contract/capability/health/policy."""

    def __init__(
        self,
        registry: Optional[WorkerRegistry] = None,
        policy_checker: Optional[Callable[[str, str], bool]] = None,
    ) -> None:
        self._registry = registry or WorkerRegistry()
        self._policy_checker = policy_checker
        self._lock = threading.RLock()
        self._history: List[RoutingDecision] = []

    @property
    def registry(self) -> WorkerRegistry:
        return self._registry

    def _is_policy_allowed(self, task_id: str, worker_id: str) -> bool:
        if self._policy_checker is None:
            return True
        try:
            return bool(self._policy_checker(task_id, worker_id))
        except Exception:
            return False

    def _worker_matches_capabilities(self, worker: RegisteredWorker, required: List[str]) -> bool:
        if not required:
            return True
        caps = set(worker.contract.capabilities)
        return all(c in caps for c in required)

    def _is_healthy(self, worker: RegisteredWorker) -> bool:
        return worker.health not in (WorkerHealth.UNAVAILABLE, WorkerHealth.DEGRADED)

    def route(self, request: RoutingRequest) -> RoutingDecision:
        request.validate()
        with self._lock:
            # 1) If preferred_worker_id specified, try it first
            if request.preferred_worker_id:
                try:
                    rw = self._registry.get(request.preferred_worker_id)
                    if self._is_healthy(rw) and self._worker_matches_capabilities(rw, request.required_capabilities):
                        if self._is_policy_allowed(request.task_id, rw.contract.worker_id):
                            decision = RoutingDecision(
                                task_id=request.task_id,
                                worker_id=rw.contract.worker_id,
                                worker_type=rw.contract.worker_type.value,
                                reason=f"preferred worker {rw.contract.worker_id!r} matched",
                            )
                            self._history.append(decision)
                            return decision
                except WorkerRegistryError:
                    pass  # preferred not found, fall through

            # 2) Find by task_type → worker_type
            preferred_type = _TASK_TYPE_TO_WORKER_TYPE.get(request.task_type.lower(), "general")

            # Collect candidates: matching type + capabilities + healthy + policy
            candidates: List[RegisteredWorker] = []
            for rw in self._registry.list():
                if rw.contract.worker_type.value != preferred_type:
                    continue
                if not self._is_healthy(rw):
                    continue
                if not self._worker_matches_capabilities(rw, request.required_capabilities):
                    continue
                if not self._is_policy_allowed(request.task_id, rw.contract.worker_id):
                    continue
                candidates.append(rw)

            if candidates:
                # Deterministic: sort by worker_id
                candidates.sort(key=lambda w: w.contract.worker_id)
                chosen = candidates[0]
                decision = RoutingDecision(
                    task_id=request.task_id,
                    worker_id=chosen.contract.worker_id,
                    worker_type=chosen.contract.worker_type.value,
                    reason=f"matched type {preferred_type!r} with capabilities {request.required_capabilities}",
                )
                self._history.append(decision)
                return decision

            # 3) Fallback: any worker with required capabilities (if policy allows fallback)
            # Only fallback if policy_checker allows it (or no checker)
            fallback_candidates: List[RegisteredWorker] = []
            for rw in self._registry.list():
                if not self._is_healthy(rw):
                    continue
                if not self._worker_matches_capabilities(rw, request.required_capabilities):
                    continue
                if not self._is_policy_allowed(request.task_id, rw.contract.worker_id):
                    continue
                fallback_candidates.append(rw)

            if fallback_candidates:
                # Only allow fallback if explicitly permitted or no policy checker
                # If policy_checker exists, it already filtered; so fallback is policy-gated
                fallback_candidates.sort(key=lambda w: w.contract.worker_id)
                chosen = fallback_candidates[0]
                is_fallback = chosen.contract.worker_type.value != preferred_type
                decision = RoutingDecision(
                    task_id=request.task_id,
                    worker_id=chosen.contract.worker_id,
                    worker_type=chosen.contract.worker_type.value,
                    reason=f"fallback to {chosen.contract.worker_type.value!r} (preferred {preferred_type!r} unavailable)",
                    is_fallback=is_fallback,
                )
                self._history.append(decision)
                return decision

            raise WorkerRouterError(
                f"no available worker for task {request.task_id!r} "
                f"(type={request.task_type!r}, capabilities={request.required_capabilities})"
            )

    def can_route(self, request: RoutingRequest) -> bool:
        try:
            self.route(request)
            return True
        except WorkerRouterError:
            return False

    def history(self) -> List[RoutingDecision]:
        with self._lock:
            return list(self._history)

    def clear_history(self) -> None:
        with self._lock:
            self._history.clear()
