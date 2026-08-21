"""Health status normalization for the Dashboard.

Ensures UNKNOWN is never displayed as healthy. Maps raw health
responses to normalized HealthStatus enum values.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Normalized health status values."""

    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

    def is_healthy(self) -> bool:
        """Only PASS is considered healthy. UNKNOWN is NOT healthy."""
        return self == HealthStatus.PASS


class ComponentHealth:
    """Health status for a single system component."""

    def __init__(
        self,
        name: str,
        status: HealthStatus,
        detail: str = "",
        latency_ms: float = 0.0,
    ) -> None:
        self.name = name
        self.status = status
        self.detail = detail
        self.latency_ms = latency_ms

    @property
    def is_healthy(self) -> bool:
        return self.status.is_healthy()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
            "latency_ms": self.latency_ms,
            "is_healthy": self.is_healthy,
        }


class HealthChecker:
    """Normalizes raw health responses into structured HealthStatus.

    AC-018-09: UNKNOWN is never displayed as healthy.
    """

    # Maps raw string values to HealthStatus
    _STATUS_MAP: dict[str, HealthStatus] = {
        "ok": HealthStatus.PASS,
        "healthy": HealthStatus.PASS,
        "pass": HealthStatus.PASS,
        "up": HealthStatus.PASS,
        "active": HealthStatus.PASS,
        "running": HealthStatus.PASS,
        "warning": HealthStatus.WARNING,
        "degraded": HealthStatus.WARNING,
        "slow": HealthStatus.WARNING,
        "error": HealthStatus.ERROR,
        "failed": HealthStatus.ERROR,
        "down": HealthStatus.ERROR,
        "unavailable": HealthStatus.ERROR,
        "crashed": HealthStatus.ERROR,
        "unknown": HealthStatus.UNKNOWN,
        "unchecked": HealthStatus.UNKNOWN,
        "none": HealthStatus.UNKNOWN,
    }

    # Known component names for the health dashboard
    COMPONENTS = [
        "runtime",
        "orchestrator",
        "database",
        "model",
        "memory",
        "workflow",
        "capability",
        "tool",
        "skill",
    ]

    @classmethod
    def normalize_status(cls, raw: str) -> HealthStatus:
        """Convert a raw status string to HealthStatus.

        Unknown strings default to UNKNOWN (fail-closed).
        """
        return cls._STATUS_MAP.get(raw.lower().strip(), HealthStatus.UNKNOWN)

    @classmethod
    def check_component(cls, name: str, raw_status: str, detail: str = "") -> ComponentHealth:
        """Normalize a single component's health."""
        status = cls.normalize_status(raw_status)
        return ComponentHealth(name=name, status=status, detail=detail)

    @classmethod
    def check_all(cls, health_data: dict[str, Any]) -> list[ComponentHealth]:
        """Normalize all component health from a raw health response.

        Returns a list of ComponentHealth for each known component.
        Components not in the response get UNKNOWN status.
        """
        results = []
        for component in cls.COMPONENTS:
            raw = health_data.get(component, "unknown")
            if isinstance(raw, dict):
                status_str = raw.get("status", "unknown")
                detail = raw.get("detail", "")
            else:
                status_str = str(raw) if raw else "unknown"
                detail = ""
            results.append(cls.check_component(component, status_str, detail))
        return results

    @classmethod
    def overall_status(cls, components: list[ComponentHealth]) -> HealthStatus:
        """Determine overall health from component list.

        - Any ERROR → ERROR
        - Any WARNING (no ERROR) → WARNING
        - All PASS → PASS
        - Otherwise → UNKNOWN
        """
        statuses = [c.status for c in components]
        if HealthStatus.ERROR in statuses:
            return HealthStatus.ERROR
        if HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        if all(s == HealthStatus.PASS for s in statuses):
            return HealthStatus.PASS
        return HealthStatus.UNKNOWN

    @classmethod
    def healthy_count(cls, components: list[ComponentHealth]) -> int:
        """Count of healthy components."""
        return sum(1 for c in components if c.is_healthy)

    @classmethod
    def unhealthy_components(cls, components: list[ComponentHealth]) -> list[ComponentHealth]:
        """Return components that are not healthy."""
        return [c for c in components if not c.is_healthy]
