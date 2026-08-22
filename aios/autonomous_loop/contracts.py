"""Autonomous Loop contracts (TASK-053)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CycleStatus(str, Enum):
    CREATED = "created"
    OBSERVING = "observing"
    PLANNING = "planning"
    VALIDATING = "validating"
    ACTING = "acting"
    EVALUATING = "evaluating"
    LEARNING = "learning"
    DECIDING = "deciding"
    COMPLETED = "completed"
    REPLANNING = "replanning"
    WAITING = "waiting"
    STOPPED = "stopped"
    FAILED = "failed"


class Decision(str, Enum):
    CONTINUE = "continue"
    REPLAN = "replan"
    WAIT = "wait"
    STOP = "stop"


class StopCondition(str, Enum):
    GOAL_COMPLETED = "goal_completed"
    POLICY_DENIED = "policy_denied"
    SAFETY_BLOCK = "safety_block"
    MAX_ITERATIONS = "max_iterations"
    MAX_COST = "max_cost"
    MAX_RUNTIME = "max_runtime"
    NO_PROGRESS = "no_progress"
    REPEATED_FAILURE = "repeated_failure"
    WORLD_STATE_INVALID = "world_state_invalid"
    DEPENDENCY_BLOCKED = "dependency_blocked"
    USER_STOP = "user_stop"


@dataclass
class CandidateLearning:
    """Learning produced by a cycle — candidate only, never auto-promoted."""
    learning_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    observation: dict[str, Any] = field(default_factory=dict)
    lesson: str = ""
    verified: bool = False
    promoted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "learning_id": self.learning_id,
            "goal_id": self.goal_id,
            "lesson": self.lesson,
            "verified": self.verified,
            "promoted": self.promoted,
        }


@dataclass
class AutonomousCycle:
    cycle_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    parent_cycle_id: str = ""
    world_state_ref: str = ""
    plan_ref: str = ""
    execution_ref: str = ""
    observation_ref: str = ""
    evaluation_ref: str = ""
    learning_ref: str = ""
    iteration: int = 0
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    status: CycleStatus = CycleStatus.CREATED
    decision: Decision | None = None
    stop_condition: StopCondition | None = None
    progress: float = 0.0
    cost: float = 0.0
    failures: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "goal_id": self.goal_id,
            "parent_cycle_id": self.parent_cycle_id,
            "iteration": self.iteration,
            "status": self.status.value,
            "decision": self.decision.value if self.decision else None,
            "stop_condition": self.stop_condition.value if self.stop_condition else None,
            "progress": self.progress,
            "cost": self.cost,
            "failures": self.failures,
        }
