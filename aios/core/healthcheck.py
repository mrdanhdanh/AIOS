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
    """Aggregate health status.

    Canonical M1 spec requires at least three distinguishable states:
    ``healthy / unhealthy / not-ready|unavailable``.

    ``DEGRADED`` is kept for backward-compatibility and is semantically
    equivalent to ``NOT_READY`` (partial failure / not ready to serve).
    """

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    NOT_READY = "NOT_READY"
    UNAVAILABLE = "UNAVAILABLE"

    @property
    def is_not_ready(self) -> bool:
        """True for NOT_READY / UNAVAILABLE / DEGRADED (spec: not-ready / unavailable)."""
        return self in (HealthStatus.NOT_READY, HealthStatus.UNAVAILABLE, HealthStatus.DEGRADED)


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

    Spec M1: must distinguish ``healthy / unhealthy / not-ready|unavailable``.
    ``DEGRADED`` is retained as an alias of ``NOT_READY`` for backward compat.

    ``not-ready`` semantics: ``HealthCheck`` starts as ready (so empty-probe
    suites stay HEALTHY — backward compat) but callers can flip readiness via
    :meth:`mark_not_ready` / :meth:`mark_ready`. When not ready, :meth:`run`
    returns ``NOT_READY`` regardless of probe outcomes — satisfying the
    requirement that "process started != runtime ready".

    ``unhealthy`` semantics: a failing probe registered with
    ``critical=True`` promotes the aggregate status to ``UNHEALTHY``; non-
    critical failures map to ``DEGRADED`` (i.e. not-ready).

    Example::

        hc = HealthCheck(config=Config())
        hc.register("db", check_database_connection, critical=True)
        result = hc.run()
        assert result.status == HealthStatus.HEALTHY
    """

    def __init__(self, config: Optional[Config] = None, *, ready: bool = True) -> None:
        self._config = config or Config()
        self._probes: Dict[str, ProbeFn] = {}
        self._critical: set[str] = set()
        self._ready: bool = ready
        self._not_ready_reason: str = ""

    # -- readiness -------------------------------------------------------

    def mark_ready(self) -> None:
        """Mark runtime as ready to serve."""
        self._ready = True
        self._not_ready_reason = ""

    def mark_not_ready(self, reason: str = "") -> None:
        """Mark runtime as not-ready / unavailable (spec requirement)."""
        self._ready = False
        self._not_ready_reason = reason

    @property
    def is_ready(self) -> bool:
        return self._ready

    def register(self, name: str, probe: ProbeFn, *, critical: bool = False) -> None:
        """Register a named probe callable.

        Args:
            critical: when True, a failure promotes aggregate status to
                UNHEALTHY (instead of DEGRADED).
        """
        self._probes[name] = probe
        if critical:
            self._critical.add(name)
        else:
            self._critical.discard(name)

    def unregister(self, name: str) -> None:
        """Remove a previously registered probe."""
        self._probes.pop(name, None)
        self._critical.discard(name)

    def run(self) -> HealthResult:
        """Execute all registered probes and return an aggregated result."""
        results: List[ProbeResult] = []
        has_failure = False
        has_critical_failure = False

        for name, probe in self._probes.items():
            try:
                probe()
                results.append(ProbeResult(name=name, healthy=True))
            except Exception as exc:
                has_failure = True
                if name in self._critical:
                    has_critical_failure = True
                msg = f"{type(exc).__name__}: {exc}"
                results.append(ProbeResult(name=name, healthy=False, message=msg))
                logger.warning("Health probe '%s' failed: %s", name, msg)

        # Not-ready takes precedence — spec: process started != runtime ready.
        if not self._ready:
            status = HealthStatus.NOT_READY
            if self._not_ready_reason:
                # Surface the reason as an extra synthetic probe so that
                # callers/evidence have visibility.
                results.append(
                    ProbeResult(name="_readiness", healthy=False, message=self._not_ready_reason)
                )
        elif not has_failure:
            status = HealthStatus.HEALTHY
        elif has_critical_failure:
            status = HealthStatus.UNHEALTHY
        else:
            # Non-critical failure → degraded / not-ready (spec: not-ready)
            status = HealthStatus.DEGRADED

        return HealthResult(status=status, probes=results)
