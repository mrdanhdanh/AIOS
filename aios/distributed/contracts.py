"""Distributed runtime contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class DistributedError(Exception): pass

class NodeState(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DRAINING = "draining"
    FAILED = "failed"

@dataclass
class RuntimeNode:
    node_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    address: str = ""
    state: NodeState = NodeState.ONLINE
    capacity: int = 100
    @property
    def is_healthy(self) -> bool: return self.state == NodeState.ONLINE
    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "name": self.name, "state": self.state.value, "capacity": self.capacity}
