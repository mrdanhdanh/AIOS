"""HA contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Any

@dataclass
class HAConfig:
    primary_node: str = ""
    replica_nodes: list = field(default_factory=list)
    health_check_interval: float = 30.0
    auto_failover: bool = True
    def to_dict(self) -> dict[str, Any]:
        return {"primary_node": self.primary_node, "replica_nodes": self.replica_nodes, "auto_failover": self.auto_failover}

@dataclass
class RecoveryPlan:
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    steps: list = field(default_factory=list)
    auto_failover: bool = True
    def to_dict(self) -> dict[str, Any]:
        return {"plan_id": self.plan_id, "steps": self.steps, "auto_failover": self.auto_failover}
