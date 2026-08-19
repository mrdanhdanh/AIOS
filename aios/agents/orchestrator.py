"""Orchestrator role.

The orchestrator drives a task through its lifecycle using the governance
interfaces. It never executes work itself; it coordinates spec-writer, critic
and reviewer, and only marks a task DONE after the unified gate passes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aios.governance.lifecycle import TaskLifecycle
from aios.governance.gates import UnifiedTaskGate


@dataclass
class AgentContext:
    """Interfaces an agent is allowed to use (no direct runtime/tool access)."""

    lifecycle: TaskLifecycle
    gate: UnifiedTaskGate
    artifacts: Dict[str, str] = field(default_factory=dict)


class Orchestrator:
    """Coordinates the lifecycle of a single task through the governance system."""

    def __init__(self, ctx: AgentContext) -> None:
        self.ctx = ctx

    def advance(self, task_id: str, to_state: str, artifacts: Optional[List[str]] = None) -> str:
        return self.ctx.lifecycle.transition(
            task_id, to_state, provided_artifacts=artifacts or []
        )

    def can_close(self, task_id: str) -> bool:
        return self.ctx.lifecycle.can_close(
            task_id, provided_artifacts=list(self.ctx.artifacts.keys())
        )

    def close_if_gate_passes(self, task_id: str) -> bool:
        # A task may only reach DONE when the unified gate passes.
        gate_result = self.ctx.gate.evaluate({})
        if not gate_result.passed:
            return False
        if not self.can_close(task_id):
            return False
        self.ctx.lifecycle.close(
            task_id, provided_artifacts=list(self.ctx.artifacts.keys())
        )
        return True
