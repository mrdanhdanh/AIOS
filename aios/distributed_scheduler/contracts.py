"""Distributed scheduler contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class LeaseState(Enum):
    HELD = "held"
    EXPIRED = "expired"
    RELEASED = "released"

@dataclass
class Lease:
    lease_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    node_id: str = ""
    resource_id: str = ""
    state: LeaseState = LeaseState.HELD
    ttl_seconds: int = 300
    def to_dict(self) -> dict[str, Any]:
        return {"lease_id": self.lease_id, "node_id": self.node_id, "resource_id": self.resource_id, "state": self.state.value}
