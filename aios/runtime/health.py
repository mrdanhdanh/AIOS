"""Runtime health model and monitor (TASK-065 hardening).

Defines the :class:`RuntimeHealth` dataclass (spec hardening contract) and a
:class:`HealthMonitor` that aggregates per-component health. Layering: runtime
layer — relative imports only; imports ``aios.core`` (unknown layer) freely.

Hardening contract (T065 §2)::

    RuntimeHealth
    ├── component
    ├── status: HEALTHY | DEGRADED | UNHEALTHY
    ├── last_check
    └── evidence_ref
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


__all__ = ["HealthStatus", "RuntimeHealth", "HealthMonitor", "HealthError"]


class HealthStatus(Enum):
    """Component health status (T065 §2)."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthError(Exception):
    """Raised on health monitor errors."""


@dataclass
class RuntimeHealth:
    """Hardening health contract (T065 §2).

    ``component`` — logical name of the monitored component.
    ``status`` — HEALTHY | DEGRADED | UNHEALTHY.
    ``last_check`` — ISO-8601 UTC timestamp of the last evaluation.
    ``evidence_ref`` — opaque reference to supporting evidence (e.g. run_id).
    """

    component: str
    status: HealthStatus = HealthStatus.HEALTHY
    last_check: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    evidence_ref: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "component": self.component,
            "status": self.status.value,
            "last_check": self.last_check,
            "evidence_ref": self.evidence_ref,
        }


class HealthMonitor:
    """Aggregates per-component :class:`RuntimeHealth`."""

    def __init__(self) -> None:
        self._health: Dict[str, RuntimeHealth] = {}
        self._lock = threading.RLock()

    def report(self, health: RuntimeHealth) -> None:
        with self._lock:
            self._health[health.component] = health

    def record(
        self,
        component: str,
        status: HealthStatus,
        evidence_ref: Optional[str] = None,
        *,
        last_check: Optional[str] = None,
    ) -> RuntimeHealth:
        h = RuntimeHealth(
            component=component,
            status=status,
            evidence_ref=evidence_ref,
            last_check=last_check or datetime.now(timezone.utc).isoformat(),
        )
        self.report(h)
        return h

    def get(self, component: str) -> Optional[RuntimeHealth]:
        with self._lock:
            return self._health.get(component)

    def snapshot(self) -> List[RuntimeHealth]:
        with self._lock:
            return list(self._health.values())

    def overall(self) -> HealthStatus:
        with self._lock:
            if not self._health:
                return HealthStatus.HEALTHY
            statuses = {h.status for h in self._health.values()}
            if HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            if HealthStatus.DEGRADED in statuses:
                return HealthStatus.DEGRADED
            return HealthStatus.HEALTHY
