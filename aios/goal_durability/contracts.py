"""Goal Durability contracts (TASK-056)."""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class InterruptionCause(str, Enum):
    GRACEFUL_PAUSE = "graceful_pause"
    PROCESS_CRASH = "process_crash"
    MACHINE_RESTART = "machine_restart"
    RUNTIME_FAILURE = "runtime_failure"
    SESSION_INTERRUPT = "session_interrupt"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"


class ResumeVerdict(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    STALE = "stale"
    INCONCLUSIVE = "inconclusive"


@dataclass
class DurableCheckpoint:
    checkpoint_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    sequence: int = 0  # monotonic, atomic commit
    created_at: float = field(default_factory=time.time)
    interruption_cause: str = ""
    goal_state: dict[str, Any] = field(default_factory=dict)
    current_subgoal: str = ""
    completed_tasks: list[str] = field(default_factory=list)
    pending_tasks: list[str] = field(default_factory=list)
    execution_graph_state: dict[str, Any] = field(default_factory=dict)
    world_state_ref: str = ""
    memory_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    policy_autonomy_state: dict[str, Any] = field(default_factory=dict)
    recovery_state: dict[str, Any] = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)
    content_hash: str = ""

    def compute_hash(self) -> str:
        payload = (
            f"{self.goal_id}|{self.sequence}|{self.current_subgoal}|"
            f"{sorted(self.completed_tasks)}|{sorted(self.pending_tasks)}|"
            f"{self.interruption_cause}|{self.world_state_ref}|"
            f"{sorted(self.evidence_refs)}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def finalize(self) -> None:
        self.content_hash = self.compute_hash()

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "goal_id": self.goal_id,
            "sequence": self.sequence,
            "interruption_cause": self.interruption_cause,
            "goal_state": dict(self.goal_state),
            "current_subgoal": self.current_subgoal,
            "completed_tasks": list(self.completed_tasks),
            "pending_tasks": list(self.pending_tasks),
            "execution_graph_state": dict(self.execution_graph_state),
            "world_state_ref": self.world_state_ref,
            "memory_refs": list(self.memory_refs),
            "artifact_refs": list(self.artifact_refs),
            "policy_autonomy_state": dict(self.policy_autonomy_state),
            "recovery_state": dict(self.recovery_state),
            "evidence_refs": list(self.evidence_refs),
            "content_hash": self.content_hash,
        }
