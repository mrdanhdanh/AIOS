"""Operations health model — fail-closed (UNKNOWN is never HEALTHY)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OpsHealthLevel(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class OpsComponentHealth:
    name: str
    level: OpsHealthLevel = OpsHealthLevel.UNKNOWN
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "level": self.level.value, "detail": self.detail}


class OperationsHealth:
    """Aggregates component health into an overall fail-closed status."""

    def __init__(self) -> None:
        self._components: list[OpsComponentHealth] = []

    def set(self, name: str, level: OpsHealthLevel, detail: str = "") -> None:
        for c in self._components:
            if c.name == name:
                c.level = level
                c.detail = detail
                return
        self._components.append(OpsComponentHealth(name=name, level=level, detail=detail))

    def overall(self) -> OpsHealthLevel:
        levels = [c.level for c in self._components]
        if not levels:
            return OpsHealthLevel.UNKNOWN
        if OpsHealthLevel.UNHEALTHY in levels:
            return OpsHealthLevel.UNHEALTHY
        if OpsHealthLevel.DEGRADED in levels or OpsHealthLevel.UNKNOWN in levels:
            return OpsHealthLevel.DEGRADED
        return OpsHealthLevel.HEALTHY

    def is_healthy(self) -> bool:
        """Fail-closed: UNKNOWN is never healthy."""
        return self.overall() == OpsHealthLevel.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall().value,
            "components": [c.to_dict() for c in self._components],
        }
