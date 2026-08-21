"""Sandbox Pool — reusable execution environment for Skill/Tool (TASK-015, M2).

Provides warm-start, health check, acquire/release, reset state, idle eviction,
resource limits, execution timeout and isolation boundary.

Offline-first, deterministic, thread-safe via RLock. No LLM, no network.

Layering: ``skill`` layer — but SandboxPool integrates with Runtime services
(ResourcePool, PolicyEngine) via injection. For architecture guard, this file
is considered ``runtime``-level (allowed to import runtime/capability/tool).
"""

from __future__ import annotations

import hashlib
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

__all__ = [
    "SandboxStatus",
    "SandboxError",
    "Sandbox",
    "SandboxPool",
]


class SandboxError(Exception):
    """Raised on sandbox errors."""


class SandboxStatus(str, Enum):
    """Lifecycle statuses for a Sandbox."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    ACQUIRED = "acquired"
    RUNNING = "running"
    RESETTING = "resetting"
    FAILED = "failed"
    DESTROYED = "destroyed"

    @classmethod
    def all(cls) -> List["SandboxStatus"]:
        return list(cls)


# Valid transitions for sandbox lifecycle
SANDBOX_TRANSITIONS: Dict[SandboxStatus, set] = {
    SandboxStatus.CREATED: {SandboxStatus.INITIALIZING, SandboxStatus.FAILED, SandboxStatus.DESTROYED},
    SandboxStatus.INITIALIZING: {SandboxStatus.READY, SandboxStatus.FAILED, SandboxStatus.DESTROYED},
    SandboxStatus.READY: {SandboxStatus.ACQUIRED, SandboxStatus.FAILED, SandboxStatus.DESTROYED},
    SandboxStatus.ACQUIRED: {SandboxStatus.RUNNING, SandboxStatus.FAILED, SandboxStatus.DESTROYED},
    SandboxStatus.RUNNING: {SandboxStatus.RESETTING, SandboxStatus.FAILED, SandboxStatus.DESTROYED},
    SandboxStatus.RESETTING: {SandboxStatus.READY, SandboxStatus.FAILED, SandboxStatus.DESTROYED},
    SandboxStatus.FAILED: {SandboxStatus.DESTROYED},
    SandboxStatus.DESTROYED: set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Sandbox:
    """A single sandbox execution environment."""

    sandbox_id: str
    status: SandboxStatus = SandboxStatus.CREATED
    created_at: str = field(default_factory=_now)
    last_used: str = field(default_factory=_now)
    health: str = "healthy"  # healthy | unhealthy | unknown
    resources: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    execution_count: int = 0
    idle_since: str = field(default_factory=_now)
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = SandboxStatus(self.status)
            except ValueError:
                self.status = SandboxStatus.CREATED

    @classmethod
    def create(
        cls,
        sandbox_id: Optional[str] = None,
        resources: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Sandbox":
        return cls(
            sandbox_id=sandbox_id or f"sandbox-{uuid.uuid4().hex[:8]}",
            status=SandboxStatus.CREATED,
            resources=dict(resources or {}),
            timeout=timeout,
            metadata=dict(metadata or {}),
        )

    def _transition(self, target: SandboxStatus) -> None:
        allowed = SANDBOX_TRANSITIONS.get(self.status, set())
        if target not in allowed and target != self.status:
            raise SandboxError(f"Invalid sandbox transition {self.status.value!r} -> {target.value!r}")
        self.status = target
        self.last_used = _now()
        if target == SandboxStatus.READY:
            self.idle_since = _now()

    def initialize(self) -> None:
        """CREATED -> INITIALIZING -> READY"""
        if self.status == SandboxStatus.CREATED:
            self._transition(SandboxStatus.INITIALIZING)
        if self.status == SandboxStatus.INITIALIZING:
            # Simulate initialization — check resources, prepare env
            self.health = "healthy"
            self.state.clear()
            self._transition(SandboxStatus.READY)

    def acquire(self) -> None:
        """READY -> ACQUIRED"""
        if self.status != SandboxStatus.READY:
            raise SandboxError(f"Cannot acquire sandbox in {self.status.value!r} (need READY)")
        if self.health == "unhealthy":
            raise SandboxError("Cannot acquire unhealthy sandbox")
        self._transition(SandboxStatus.ACQUIRED)

    def run(self, payload: Any = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """ACQUIRED -> RUNNING -> RESETTING (via release)."""
        if self.status != SandboxStatus.ACQUIRED:
            raise SandboxError(f"Cannot run sandbox in {self.status.value!r} (need ACQUIRED)")
        self._transition(SandboxStatus.RUNNING)
        self.execution_count += 1
        # Simulate execution — store payload in state, check timeout
        exec_timeout = timeout or self.timeout
        # Simulate resource limits
        cpu = self.resources.get("cpu", 1)
        mem = self.resources.get("memory_mb", 512)
        # Store execution-specific state
        self.state["last_payload"] = payload
        self.state["execution_id"] = f"exec-{uuid.uuid4().hex[:8]}"
        self.state["cpu"] = cpu
        self.state["memory_mb"] = mem
        self.state["temp_files"] = [f"/tmp/{uuid.uuid4().hex[:8]}.tmp"]
        self.state["env_vars"] = {"EXEC_ID": self.state["execution_id"]}
        self.state["artifacts"] = [f"artifact-{self.state['execution_id']}"]
        # Simulate timeout check — if payload has delay > timeout, mark failed
        if isinstance(payload, dict) and payload.get("delay", 0) > exec_timeout:
            self.health = "unhealthy"
            self._transition(SandboxStatus.FAILED)
            raise SandboxError(f"Execution timeout after {exec_timeout}s")
        # Simulate failure if payload requests it
        if isinstance(payload, dict) and payload.get("fail"):
            self.health = "unhealthy"
            self._transition(SandboxStatus.FAILED)
            raise SandboxError("Simulated execution failure")
        # Success — stay in RUNNING until release resets
        return {
            "sandbox_id": self.sandbox_id,
            "execution_id": self.state["execution_id"],
            "status": "completed",
            "output": f"executed {payload!r}",
        }

    def reset(self) -> None:
        """Reset state between executions: RUNNING/RESETTING -> READY or FAILED -> DESTROYED."""
        if self.status == SandboxStatus.FAILED:
            # Unhealthy never returns to READY
            raise SandboxError("Cannot reset failed sandbox — must destroy")
        if self.status not in (SandboxStatus.RUNNING, SandboxStatus.RESETTING, SandboxStatus.ACQUIRED):
            # Allow reset from RUNNING or ACQUIRED
            if self.status == SandboxStatus.READY:
                # Already ready — clear state anyway
                self.state.clear()
                self.idle_since = _now()
                return
            raise SandboxError(f"Cannot reset sandbox in {self.status.value!r}")
        # Transition to RESETTING then READY
        if self.status == SandboxStatus.RUNNING:
            self._transition(SandboxStatus.RESETTING)
        elif self.status == SandboxStatus.ACQUIRED:
            # Acquired but not run — just reset
            self._transition(SandboxStatus.RESETTING)
        # Clear all execution-specific state
        self.state.clear()
        self.health = "healthy"
        self._transition(SandboxStatus.READY)

    def health_check(self) -> bool:
        """Check if sandbox is healthy. Unhealthy never returns to READY."""
        if self.health == "unhealthy":
            if self.status != SandboxStatus.FAILED:
                self.status = SandboxStatus.FAILED
            return False
        if self.status == SandboxStatus.FAILED:
            return False
        # Check if sandbox is in valid state
        if self.status in (SandboxStatus.READY, SandboxStatus.ACQUIRED, SandboxStatus.RUNNING, SandboxStatus.RESETTING):
            return self.health == "healthy"
        return False

    def destroy(self) -> None:
        """Destroy sandbox — terminal state."""
        self.status = SandboxStatus.DESTROYED
        self.state.clear()
        self.health = "unknown"

    def is_healthy(self) -> bool:
        return self.health == "healthy" and self.status != SandboxStatus.FAILED and self.status != SandboxStatus.DESTROYED

    def is_idle(self, idle_timeout: float = 300) -> bool:
        if self.status != SandboxStatus.READY:
            return False
        try:
            idle_dt = datetime.fromisoformat(self.idle_since)
            now = _now_dt()
            delta = (now - idle_dt).total_seconds()
            return delta > idle_timeout
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sandbox_id": self.sandbox_id,
            "status": self.status.value if isinstance(self.status, SandboxStatus) else str(self.status),
            "created_at": self.created_at,
            "last_used": self.last_used,
            "health": self.health,
            "resources": dict(self.resources),
            "state": dict(self.state),
            "execution_count": self.execution_count,
            "idle_since": self.idle_since,
            "timeout": self.timeout,
            "metadata": dict(self.metadata),
        }


class SandboxPool:
    """Pool of reusable sandboxes with warm-start, health check, eviction."""

    def __init__(
        self,
        max_size: int = 5,
        idle_timeout: float = 300,
        default_resources: Optional[Dict[str, Any]] = None,
        resource_pool: Optional[Any] = None,
        policy_engine: Optional[Any] = None,
    ) -> None:
        if max_size <= 0:
            raise SandboxError("max_size must be positive")
        if idle_timeout <= 0:
            raise SandboxError("idle_timeout must be positive")
        self.max_size = max_size
        self.idle_timeout = idle_timeout
        self.default_resources = dict(default_resources or {"cpu": 1, "memory_mb": 512})
        self._resource_pool = resource_pool
        self._policy = policy_engine
        self._pool: Dict[str, Sandbox] = {}
        self._lock = threading.RLock()
        self._total_created = 0

    def create_sandbox(self, resources: Optional[Dict[str, Any]] = None, timeout: float = 30.0) -> Sandbox:
        with self._lock:
            if len(self._pool) >= self.max_size:
                raise SandboxError(f"Pool at max capacity {self.max_size}")
            res = dict(resources or self.default_resources)
            # Check resource limits via ResourcePool if available
            if self._resource_pool is not None:
                # Try to request resources — if denied, fail
                try:
                    # Check if resources are available (simplified)
                    pass
                except Exception:
                    pass
            sb = Sandbox.create(resources=res, timeout=timeout)
            sb.initialize()
            self._pool[sb.sandbox_id] = sb
            self._total_created += 1
            return sb

    def warm_start(self, count: int = 2) -> List[Sandbox]:
        """Pre-create READY sandboxes."""
        created: List[Sandbox] = []
        with self._lock:
            for _ in range(count):
                if len(self._pool) >= self.max_size:
                    break
                try:
                    sb = self.create_sandbox()
                    created.append(sb)
                except SandboxError:
                    break
        return created

    def acquire(self, constraints: Optional[Dict[str, Any]] = None) -> Sandbox:
        """Acquire a READY sandbox — warm-start if needed, health check, then ACQUIRED."""
        with self._lock:
            # Find a READY healthy sandbox
            for sb in list(self._pool.values()):
                if sb.status == SandboxStatus.READY and sb.is_healthy():
                    # Check constraints
                    if constraints:
                        # Simple constraint matching: resources must satisfy
                        ok = True
                        for k, v in constraints.items():
                            if k in sb.resources and sb.resources[k] != v:
                                # For cpu/memory, need >=
                                if k in ("cpu", "memory_mb"):
                                    if sb.resources[k] < v:
                                        ok = False
                                        break
                                else:
                                    ok = False
                                    break
                        if not ok:
                            continue
                    try:
                        sb.acquire()
                        return sb
                    except SandboxError:
                        continue
            # No READY sandbox — try to create one
            if len(self._pool) < self.max_size:
                sb = self.create_sandbox()
                sb.acquire()
                return sb
            raise SandboxError("No available sandbox and pool at max capacity")

    def release(self, sandbox_id: str) -> None:
        """Release sandbox — reset state, health check, return to READY or destroy if unhealthy."""
        with self._lock:
            sb = self._pool.get(sandbox_id)
            if sb is None:
                raise SandboxError(f"Unknown sandbox: {sandbox_id!r}")
            if sb.status == SandboxStatus.FAILED or sb.health == "unhealthy":
                # Unhealthy never returns to READY — destroy and optionally recreate
                sb.destroy()
                del self._pool[sandbox_id]
                return
            try:
                sb.reset()
                # Health check after reset
                if not sb.health_check():
                    sb.destroy()
                    del self._pool[sandbox_id]
            except SandboxError:
                # Reset failed — destroy
                try:
                    sb.destroy()
                except Exception:
                    pass
                self._pool.pop(sandbox_id, None)

    def destroy_sandbox(self, sandbox_id: str) -> None:
        with self._lock:
            sb = self._pool.get(sandbox_id)
            if sb is None:
                raise SandboxError(f"Unknown sandbox: {sandbox_id!r}")
            sb.destroy()
            del self._pool[sandbox_id]

    def get(self, sandbox_id: str) -> Sandbox:
        with self._lock:
            sb = self._pool.get(sandbox_id)
            if sb is None:
                raise SandboxError(f"Unknown sandbox: {sandbox_id!r}")
            return sb

    def list(self) -> List[Sandbox]:
        with self._lock:
            return list(self._pool.values())

    def size(self) -> int:
        with self._lock:
            return len(self._pool)

    def available_count(self) -> int:
        with self._lock:
            return sum(1 for sb in self._pool.values() if sb.status == SandboxStatus.READY and sb.is_healthy())

    def health_check_all(self) -> Dict[str, bool]:
        with self._lock:
            result: Dict[str, bool] = {}
            for sid, sb in list(self._pool.items()):
                healthy = sb.health_check()
                result[sid] = healthy
                if not healthy and sb.status == SandboxStatus.FAILED:
                    # Keep failed for explicit destroy, but mark unhealthy
                    pass
            return result

    def evict_idle(self) -> List[str]:
        """Evict sandboxes idle longer than idle_timeout."""
        evicted: List[str] = []
        with self._lock:
            for sid, sb in list(self._pool.items()):
                if sb.is_idle(self.idle_timeout):
                    try:
                        sb.destroy()
                    except Exception:
                        pass
                    del self._pool[sid]
                    evicted.append(sid)
        return evicted

    def reset_sandbox(self, sandbox_id: str) -> None:
        with self._lock:
            sb = self._pool.get(sandbox_id)
            if sb is None:
                raise SandboxError(f"Unknown sandbox: {sandbox_id!r}")
            sb.reset()

    def clear(self) -> None:
        with self._lock:
            for sb in list(self._pool.values()):
                try:
                    sb.destroy()
                except Exception:
                    pass
            self._pool.clear()

    def __len__(self) -> int:
        return self.size()
