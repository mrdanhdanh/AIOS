"""Unified Control Center — aggregates state from all AIOS planes (TASK-237, M34).

The Control Center is a READ-ONLY aggregation layer. It pulls a snapshot of
state from every plane (Goals, Executions, Agents, Plans, Coding, Evidence,
Verification, Autonomy, Resources, Policies, Artifacts, Failures, Recovery,
System Health) into one structured view. The frontend only renders; no
business logic lives here.

Fail-closed: each plane is collected independently; a failing plane yields an
error entry rather than crashing the whole snapshot (T001 Rule 5 provenance,
deterministic, no parallel control system).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class PlaneSnapshot:
    """A single plane's state (fail-isolated)."""

    name: str
    status: str = "ok"  # ok | empty | error
    data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "data": dict(self.data),
            "error": self.error,
        }


@dataclass
class ControlCenterView:
    """Unified, read-only snapshot of the whole system."""

    system_health: str = "unknown"
    planes: Dict[str, PlaneSnapshot] = field(default_factory=dict)

    @property
    def plane_count(self) -> int:
        return len(self.planes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_health": self.system_health,
            "planes": {k: v.to_dict() for k, v in self.planes.items()},
            "plane_count": len(self.planes),
        }


class ControlCenterAggregator:
    """Collects a snapshot from every plane (fail-closed per plane)."""

    PLANES: List[str] = [
        "goals",
        "executions",
        "agents",
        "plans",
        "coding",
        "evidence",
        "verification",
        "autonomy",
        "resources",
        "policies",
        "artifacts",
        "failures",
        "recovery",
        "system_health",
    ]

    def __init__(self, collectors: Dict[str, Callable[[], Any]] | None = None) -> None:
        # collectors: plane_name -> callable() -> dict
        self._collectors: Dict[str, Callable[[], Any]] = collectors or {}

    def register(self, plane: str, collector: Callable[[], Any]) -> None:
        self._collectors[plane] = collector

    def _collect_plane(self, name: str) -> PlaneSnapshot:
        collector = self._collectors.get(name)
        if collector is None:
            return PlaneSnapshot(name=name, status="empty", data={})
        try:
            data = collector()
            if isinstance(data, PlaneSnapshot):
                return data
            if isinstance(data, dict):
                return PlaneSnapshot(name=name, status="ok", data=data)
            return PlaneSnapshot(name=name, status="ok", data={"value": data})
        except Exception as exc:  # fail-isolated: never crash the snapshot
            return PlaneSnapshot(name=name, status="error", error=str(exc))

    def snapshot(self, system_health: str = "unknown") -> ControlCenterView:
        """Build the unified view. Deterministic for the same collectors."""
        view = ControlCenterView(system_health=system_health)
        for name in self.PLANES:
            view.planes[name] = self._collect_plane(name)
        return view
