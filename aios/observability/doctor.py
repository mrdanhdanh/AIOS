"""System health doctor.

AC-021-05: Doctor distinguishes PASS/WARNING/ERROR/UNKNOWN.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class HealthLevel(str, Enum):
    """Health levels."""
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

    def is_healthy(self) -> bool:
        return self == HealthLevel.PASS


@dataclass
class ComponentReport:
    """Health report for a single component."""

    name: str
    level: HealthLevel
    detail: str = ""
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "level": self.level.value,
            "detail": self.detail,
            "latency_ms": self.latency_ms,
            "is_healthy": self.level.is_healthy(),
        }


@dataclass
class HealthReport:
    """Overall health report."""

    overall: HealthLevel = HealthLevel.UNKNOWN
    components: list[ComponentReport] = field(default_factory=list)
    healthy_count: int = 0
    unhealthy_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall.value,
            "components": [c.to_dict() for c in self.components],
            "healthy_count": self.healthy_count,
            "unhealthy_count": self.unhealthy_count,
        }


CheckFunc = Callable[[], ComponentReport]


class DoctorService:
    """System health doctor with component checks.

    AC-021-05: Distinguishes PASS/WARNING/ERROR/UNKNOWN.
    """

    def __init__(self) -> None:
        self._checks: list[tuple[str, CheckFunc]] = []

    def register(self, name: str, check_fn: CheckFunc) -> None:
        """Register a health check."""
        self._checks.append((name, check_fn))

    def check_all(self) -> HealthReport:
        """Run all health checks."""
        components: list[ComponentReport] = []
        for name, check_fn in self._checks:
            try:
                report = check_fn()
                components.append(report)
            except Exception as e:
                components.append(ComponentReport(
                    name=name,
                    level=HealthLevel.ERROR,
                    detail=f"Check failed: {e}",
                ))

        overall = self._compute_overall(components)
        healthy = sum(1 for c in components if c.level.is_healthy())

        return HealthReport(
            overall=overall,
            components=components,
            healthy_count=healthy,
            unhealthy_count=len(components) - healthy,
        )

    def _compute_overall(self, components: list[ComponentReport]) -> HealthLevel:
        levels = [c.level for c in components]
        if HealthLevel.ERROR in levels:
            return HealthLevel.ERROR
        if HealthLevel.WARNING in levels:
            return HealthLevel.WARNING
        if all(l == HealthLevel.PASS for l in levels):
            return HealthLevel.PASS
        return HealthLevel.UNKNOWN
