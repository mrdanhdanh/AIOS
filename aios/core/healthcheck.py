"""Lightweight health probe aggregation.

A :class:`HealthCheck` aggregates registered probes and returns a structured
:class:`HealthResult`.  Probes are registered at init time so the healthcheck
is extensible by later tasks without modifying this module.

Probe protocol::

    A probe is any callable that returns None (healthy) or raises Exception
    (unhealthy).  Example::

        def my_probe() -> None:
            ...
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .config import Config

logger = logging.getLogger(__name__)

__all__ = ["HealthCheck", "HealthResult", "HealthStatus", "ProbeFn"]

# Type alias for a probe function (no args, returns None or raises).
ProbeFn = Callable[[], None]


class HealthStatus(str, Enum):
    """Aggregate health status."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass(frozen=True)
class ProbeResult:
    """Result of a single probe."""

    name: str
    healthy: bool
    message: str = ""


@dataclass(frozen=True)
class HealthResult:
    """Aggregated health-check result."""

    status: HealthStatus
    probes: List[ProbeResult] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "probes": [
                {"name": p.name, "healthy": p.healthy, "message": p.message}
                for p in self.probes
            ],
        }


class HealthCheck:
    """Aggregates probes and produces a :class:`HealthResult`.

    Example::

        hc = HealthCheck(config=Config())
        hc.register("db", check_database_connection)
        result = hc.run()
        assert result.status == HealthStatus.HEALTHY
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        self._config = config or Config()
        self._probes: Dict[str, ProbeFn] = {}

    def register(self, name: str, probe: ProbeFn) -> None:
        """Register a named probe callable."""
        self._probes[name] = probe

    def unregister(self, name: str) -> None:
        """Remove a previously registered probe."""
        self._probes.pop(name, None)

    def run(self) -> HealthResult:
        """Execute all registered probes and return an aggregated result."""
        results: List[ProbeResult] = []
        all_healthy = True

        for name, probe in self._probes.items():
            try:
                probe()
                results.append(ProbeResult(name=name, healthy=True))
            except Exception as exc:
                all_healthy = False
                msg = f"{type(exc).__name__}: {exc}"
                results.append(ProbeResult(name=name, healthy=False, message=msg))
                logger.warning("Health probe '%s' failed: %s", name, msg)

        if all_healthy:
            status = HealthStatus.HEALTHY
        else:
            # If any probe failed, we are at least DEGRADED.
            status = HealthStatus.DEGRADED

        return HealthResult(status=status, probes=results)
