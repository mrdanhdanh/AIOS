"""TASK-202 — Autonomous Guardrails (M26).

Autonomous guardrails for coding actions, converging Safety Controller (T153)
and Autonomy Safety (T067). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from aios.coding_edition._common import CodingEditionError, _hash


class GuardrailVerdict(str, Enum):
    """Guardrail outcome (T202)."""

    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Guardrail:
    """A single deterministic guardrail (T202)."""

    guardrail_id: str
    description: str
    forbidden_prefix: Optional[str] = None  # action prefix that is always blocked
    max_autonomy: float = 1.0  # max autonomy level this guardrail permits

    def __post_init__(self) -> None:
        if not self.guardrail_id:
            raise CodingEditionError("guardrail_id is required (T001 Rule 1, immutable).")

    def check(self, action: str, autonomy: float) -> Tuple[bool, str]:
        if self.forbidden_prefix and action.startswith(self.forbidden_prefix):
            return False, f"action matches forbidden prefix '{self.forbidden_prefix}'"
        if autonomy > self.max_autonomy:
            return False, f"autonomy {autonomy} exceeds max {self.max_autonomy}"
        return True, "ok"


class GuardrailSet:
    """Deterministic autonomous guardrail set (T202)."""

    def __init__(self, guardrails: Optional[List[Guardrail]] = None) -> None:
        self._guardrails: List[Guardrail] = list(guardrails or [])

    def add(self, g: Guardrail) -> None:
        self._guardrails.append(g)

    def check(self, action: str, autonomy: float = 1.0) -> Tuple[GuardrailVerdict, List[str]]:
        """Check an action against all guardrails (fail-closed)."""
        if not self._guardrails:
            return GuardrailVerdict.UNKNOWN, ["no guardrails defined"]
        blocked: List[str] = []
        for g in self._guardrails:
            ok, reason = g.check(action, autonomy)
            if not ok:
                blocked.append(f"{g.guardrail_id}:{reason}")
        if blocked:
            return GuardrailVerdict.BLOCKED, blocked
        return GuardrailVerdict.ALLOWED, []

    def guardrail_hash(self, action: str, autonomy: float = 1.0) -> str:
        v, _ = self.check(action, autonomy)
        return _hash(f"{action}|{autonomy:.2f}|{v.value}")
