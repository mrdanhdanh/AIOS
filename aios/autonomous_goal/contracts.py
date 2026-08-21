"""Autonomous goal contracts."""
from __future__ import annotations
import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class GoalStatus(Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class Goal:
    goal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    status: GoalStatus = GoalStatus.CREATED
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict[str, Any]:
        return {"goal_id": self.goal_id, "title": self.title, "status": self.status.value}

@dataclass
class GoalPlan:
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    steps: list = field(default_factory=list)
    estimated_effort: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"plan_id": self.plan_id, "goal_id": self.goal_id, "steps": self.steps}
