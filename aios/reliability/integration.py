"""Reliability integration (TASK-069).

- Health probe integration via ``aios.core.healthcheck`` (best-effort import).
- Optional hooks into Durable (T066) and Kill Switch (T068) — imported lazily so
  the reliability package never hard-depends on packages that may be absent.
"""

from __future__ import annotations

from typing import Any, Optional

from aios.reliability.slo import ErrorBudgetExhausted, SLORegistry

try:  # pragma: no cover - import shape depends on install
    from aios.core.healthcheck import HealthCheck

    _HAVE_HEALTH = True
except Exception:  # pragma: no cover
    _HAVE_HEALTH = False
    HealthCheck = Any  # type: ignore


class ReliabilityProbe:
    """A health probe that fails when any SLO error budget is exhausted."""

    def __init__(self, registry: SLORegistry) -> None:
        self._registry = registry

    def __call__(self) -> None:
        for name, metric in self._registry._metrics.items():
            if metric.error_budget_remaining <= 0.0:
                raise ErrorBudgetExhausted(f"SLO {name!r} error budget exhausted")


def register_reliability_probes(healthcheck: Any, registry: SLORegistry) -> None:
    """Register a reliability probe on a ``HealthCheck`` instance (no-op if unavailable)."""
    if not _HAVE_HEALTH:
        return
    if isinstance(healthcheck, HealthCheck):
        healthcheck.register("reliability", ReliabilityProbe(registry))


def build_kill_switch_bridge() -> Optional[Any]:
    """Best-effort bridge to Kill Switch (T068) for fail-closed halt on exhaustion."""
    try:  # pragma: no cover - optional dependency
        from aios.kill_switch.controller import KillSwitchController

        return KillSwitchController()
    except Exception:  # pragma: no cover
        return None
