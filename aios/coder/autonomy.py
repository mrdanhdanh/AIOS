"""Autonomy Level + Permission Integration (TASK-132, M19).

Maps an autonomy level to the set of coder operations a coder agent may perform,
and integrates with the permission boundary (T113). Higher autonomy unlocks more
capabilities, but every operation is checked against the level's permission set
before execution (fail-closed: denied op -> PermissionError, never silently
allowed). Provenance is recorded on every decision (T001 Rule 5).
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Set


class AutonomyLevel(str, Enum):
    SUPERVISED = "SUPERVISED"      # plan + review only; no apply/patch
    ASSISTED = "ASSISTED"          # generate + review; apply requires approval
    AUTONOMOUS = "AUTONOMOUS"      # generate + apply + patch


class PermissionError_(Exception):
    """Raised when an operation is denied by the autonomy/permission boundary."""


# Operations a coder agent may request.
OP_PLAN = "plan"
OP_GENERATE = "generate"
OP_REVIEW = "review"
OP_APPLY = "apply"
OP_PATCH = "patch"

# Allowed operations per autonomy level (fail-closed: anything not listed -> denied).
_LEVEL_OPS: Dict[AutonomyLevel, Set[str]] = {
    AutonomyLevel.SUPERVISED: {OP_PLAN, OP_REVIEW},
    AutonomyLevel.ASSISTED: {OP_PLAN, OP_GENERATE, OP_REVIEW},
    AutonomyLevel.AUTONOMOUS: {OP_PLAN, OP_GENERATE, OP_REVIEW, OP_APPLY, OP_PATCH},
}


@dataclass
class PermissionDecision:
    decision_id: str
    agent_id: str
    level: AutonomyLevel
    operation: str
    allowed: bool
    reason: str
    evidence_id: str
    content_hash: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "agent_id": self.agent_id,
            "level": self.level.value,
            "operation": self.operation,
            "allowed": self.allowed,
            "reason": self.reason,
            "evidence_id": self.evidence_id,
            "content_hash": self.content_hash,
            "timestamp": self.timestamp,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class AutonomyPermissionBroker:
    """Integrates autonomy level with the permission boundary (T132 / T113)."""

    def __init__(self, agent_id: str, level: AutonomyLevel) -> None:
        if not agent_id:
            raise PermissionError_("agent_id is required (T001 Rule 1).")
        self._agent_id = agent_id
        self._level = level

    @property
    def level(self) -> AutonomyLevel:
        return self._level

    def set_level(self, level: AutonomyLevel) -> None:
        self._level = level

    def check(self, operation: str, policy_ok: bool = True) -> PermissionDecision:
        """Check whether ``operation`` is permitted at the current level.

        Fail-closed: denied (unknown op, not in level set, or policy reject) ->
        allowed=False, never silently permitted. Provenance recorded (T001).
        """
        allowed_ops = _LEVEL_OPS.get(self._level, set())
        if not policy_ok:
            reason = "policy rejected (T113)"
            allowed = False
        elif operation not in allowed_ops:
            reason = f"operation '{operation}' not permitted at level {self._level.value}"
            allowed = False
        else:
            reason = "permitted"
            allowed = True

        blob = f"{self._agent_id}:{self._level.value}:{operation}:{allowed}"
        return PermissionDecision(
            decision_id=f"perm-{uuid.uuid4().hex[:12]}",
            agent_id=self._agent_id,
            level=self._level,
            operation=operation,
            allowed=allowed,
            reason=reason,
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
            content_hash=_hash(blob),
            timestamp=_now(),
        )

    def require(self, operation: str, policy_ok: bool = True) -> PermissionDecision:
        """Like ``check`` but raise on denial (fail-closed)."""
        decision = self.check(operation, policy_ok=policy_ok)
        if not decision.allowed:
            raise PermissionError_(decision.reason)
        return decision
