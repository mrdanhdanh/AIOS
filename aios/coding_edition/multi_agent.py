"""TASK-208 — Multi-Agent Coding (M26).

Coordinate multiple coding agents, converging Multi-Agent Autonomy (T059) and
Coder (T125). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

from aios.coding_edition._common import CodingEditionError, _hash


class AgentRole(str, Enum):
    """Roles in a multi-agent coding team (T208)."""

    PLANNER = "PLANNER"
    CODER = "CODER"
    REVIEWER = "REVIEWER"
    VERIFIER = "VERIFIER"


@dataclass
class AgentAssignment:
    """An immutable-by-id agent assignment (T208)."""

    assignment_id: str
    agent_id: str
    role: AgentRole
    task: str

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise CodingEditionError("agent_id is required (T001 Rule 1, immutable).")
        if not self.task:
            raise CodingEditionError("task is required.")


class MultiAgentCoordinator:
    """Deterministic multi-agent coding coordinator (T208)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"ma-{uuid.uuid4().hex[:12]}"
        self._assignments: List[AgentAssignment] = []

    @property
    def run_id(self) -> str:
        return self._run_id

    def assign(self, agent_id: str, role: AgentRole, task: str) -> AgentAssignment:
        """Assign a task to an agent (fail-closed)."""
        a = AgentAssignment(
            assignment_id=f"as-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            role=role,
            task=task,
        )
        self._assignments.append(a)
        return a

    def detect_conflict(self) -> List[str]:
        """Detect two agents editing the same task (deterministic)."""
        seen: Dict[str, str] = {}
        conflicts: List[str] = []
        for a in self._assignments:
            if a.task in seen and seen[a.task] != a.agent_id:
                conflicts.append(a.task)
            seen[a.task] = a.agent_id
        return sorted(set(conflicts))

    def coordinator_hash(self) -> str:
        payload = "|".join(f"{a.agent_id}:{a.role.value}:{a.task}" for a in self._assignments)
        return _hash(f"{self._run_id}|{payload}")
