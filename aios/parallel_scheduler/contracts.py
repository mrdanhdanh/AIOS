"""Parallel scheduler contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class JoinPolicy(str, Enum):
    ALL_SUCCESS = "all_success"
    ANY_SUCCESS = "any_success"
    ALL_COMPLETED = "all_completed"


class DispatchDecision(str, Enum):
    """Decision for dispatching a node."""

    READY = "ready"
    WAITING_DEPENDENCY = "waiting_dependency"
    WAITING_RESOURCE = "waiting_resource"
    WAITING_POLICY = "waiting_policy"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class SchedulerState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScheduledNode:
    node_id: str = ""
    state: str = "pending"
    dependencies: list[str] = field(default_factory=list)
    dispatch_time: float = 0.0
    completion_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "state": self.state, "dependencies": self.dependencies}
