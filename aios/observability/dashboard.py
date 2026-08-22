"""Dashboard integration — projects real runtime/health state into a
dashboard-ready snapshot.

This is a *read-only projection* of true state (AC-021-10). It does not
become a control plane: it never issues commands, mutates state, or bypasses
the runtime/permission/policy boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.observability.health_api import HealthAPI, SystemHealth
from aios.observability.metrics import MetricSnapshot, MetricsCollector


@dataclass
class DashboardSnapshot:
    """A dashboard-ready projection of real system state."""

    health: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    architecture_status: str = "unknown"
    violation_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "health": self.health,
            "metrics": self.metrics,
            "architecture_status": self.architecture_status,
            "violation_count": self.violation_count,
        }


class DashboardIntegration:
    """Builds dashboard snapshots from live health + metrics surfaces."""

    def __init__(
        self,
        health_api: HealthAPI | None = None,
        metrics: MetricsCollector | None = None,
    ) -> None:
        self._health = health_api or HealthAPI()
        self._metrics = metrics or MetricsCollector()

    def snapshot(self) -> DashboardSnapshot:
        system: SystemHealth = self._health.get_health()
        snapshot_metrics: MetricSnapshot = self._metrics.snapshot()
        arch = system.architecture
        return DashboardSnapshot(
            health=system.to_dict(),
            metrics=snapshot_metrics.to_dict(),
            architecture_status=(
                "fail" if (arch and arch.violations) else "pass"
            ),
            violation_count=len(system.violations),
        )
