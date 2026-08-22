"""HA health state machine — fail-closed (UNKNOWN is never HEALTHY)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthState(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DRAINED = "drained"
    UNHEALTHY = "unhealthy"


@dataclass
class NodeHealth:
    node_id: str
    state: HealthState = HealthState.UNKNOWN
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "state": self.state.value, "detail": self.detail}


class HealthStateMachine:
    """Tracks node health with a fail-closed state machine."""

    def __init__(self) -> None:
        self._nodes: dict[str, NodeHealth] = {}

    def register(self, node_id: str) -> NodeHealth:
        node = NodeHealth(node_id=node_id, state=HealthState.UNKNOWN)
        self._nodes[node_id] = node
        return node

    def set_state(self, node_id: str, state: HealthState, detail: str = "") -> NodeHealth:
        node = self._nodes.get(node_id) or self.register(node_id)
        node.state = state
        node.detail = detail
        return node

    def is_healthy(self, node_id: str) -> bool:
        """Fail-closed: UNKNOWN is NOT healthy."""
        node = self._nodes.get(node_id)
        return node is not None and node.state == HealthState.HEALTHY

    def status(self) -> dict[str, Any]:
        return {nid: n.to_dict() for nid, n in self._nodes.items()}
