"""Health API — aggregates runtime, doctor and architecture health into a
unified, fail-closed system health surface.

This module is a *read/aggregation* surface only. It never mutates runtime
state, schedules work, or bypasses the control plane (AC-021-10).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.observability.arch_health import (
    ArchitectureHealth,
    ArchitectureHealthReport,
    ViolationReport,
)
from aios.observability.doctor import (
    ComponentReport,
    DoctorService,
    HealthLevel,
    HealthReport,
)


@dataclass
class SystemHealth:
    """Unified system health snapshot."""

    overall: HealthLevel = HealthLevel.UNKNOWN
    doctor: HealthReport | None = None
    architecture: ArchitectureHealthReport | None = None
    components: list[ComponentReport] = field(default_factory=list)
    violations: list[ViolationReport] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall.value,
            "doctor": self.doctor.to_dict() if self.doctor else None,
            "architecture": (
                self.architecture.to_dict() if self.architecture else None
            ),
            "components": [c.to_dict() for c in self.components],
            "violations": [v.to_dict() for v in self.violations],
        }


class HealthAPI:
    """Aggregates health from doctor + architecture health into one surface.

    Fail-closed: any ERROR, any critical architecture violation, or UNKNOWN
    component prevents an overall PASS (AC-021-05, AC-021-10).
    """

    def __init__(
        self,
        doctor: DoctorService | None = None,
        architecture_health: ArchitectureHealth | None = None,
    ) -> None:
        self._doctor = doctor or DoctorService()
        self._arch = architecture_health or ArchitectureHealth()

    def get_health(self) -> SystemHealth:
        doctor_report = self._doctor.check_all()
        arch_report = self._arch.get_report()

        violations = list(arch_report.violations)
        critical = any(
            v.severity.value == "critical" for v in violations
        )

        if doctor_report.overall == HealthLevel.ERROR or critical:
            overall = HealthLevel.ERROR
        elif (
            doctor_report.overall == HealthLevel.UNKNOWN
            or doctor_report.overall == HealthLevel.WARNING
            or any(v.severity.value in ("high", "medium") for v in violations)
        ):
            overall = (
                HealthLevel.WARNING
                if doctor_report.overall != HealthLevel.UNKNOWN
                else HealthLevel.UNKNOWN
            )
        else:
            overall = HealthLevel.PASS

        return SystemHealth(
            overall=overall,
            doctor=doctor_report,
            architecture=arch_report,
            components=doctor_report.components,
            violations=violations,
        )

    def is_healthy(self) -> bool:
        """Fail-closed: UNKNOWN is never healthy."""
        return self.get_health().overall == HealthLevel.PASS

    def register_check(self, name: str, check: Callable[[], ComponentReport]) -> None:
        """Allow callers to register an additional component health check."""
        self._doctor.register(name, check)
