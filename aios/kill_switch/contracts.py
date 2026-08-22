"""Kill Switch contracts (TASK-068).

Emergency stop (global halt) mechanism. Fail-closed by design: no layer may
ignore or skip a halt signal. Every halt writes audit evidence with full
provenance (Rule 5).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Protocol


class HaltSource(str, Enum):
    """Who/what issued the halt."""

    MANUAL = "manual"
    POLICY = "policy"
    SAFETY = "safety"


class HaltScope(str, Enum):
    """How far the halt propagates."""

    GLOBAL = "global"
    GOAL = "goal"
    LOOP = "loop"


class HaltViolation(Exception):
    """Raised when a halt cannot be enforced fail-closed (e.g. a layer skips)."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class HaltSignal:
    """Immutable emergency-stop signal broadcast to all active execution contexts."""

    source: HaltSource
    scope: HaltScope
    issued_at: str
    reason: str
    evidence_ref: str = ""
    signal_id: str = field(default_factory=lambda: "halt-" + _now())
    target_id: str = ""  # specific goal/loop id for GOAL/LOOP scope

    def __post_init__(self) -> None:
        if not isinstance(self.source, HaltSource):
            self.source = HaltSource(self.source)
        if not isinstance(self.scope, HaltScope):
            self.scope = HaltScope(self.scope)
        if not self.reason:
            raise ValueError("HaltSignal.reason must be non-empty")
        if not self.issued_at:
            self.issued_at = _now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "source": self.source.value,
            "scope": self.scope.value,
            "issued_at": self.issued_at,
            "reason": self.reason,
            "evidence_ref": self.evidence_ref,
            "target_id": self.target_id,
        }

    def canonical(self) -> str:
        """Deterministic canonical serialization (used for hashing / evidence)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


@dataclass
class DrainResult:
    """Result of gracefully draining a single execution context."""

    context_id: str
    context_type: str
    drained: bool
    persisted_keys: List[str] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)
    error: str = ""


@dataclass
class HaltState:
    """Recorded state of a halt (persisted + audited)."""

    signal: HaltSignal
    affected_contexts: List[str]
    drained_contexts: List[str]
    halted_at: str
    evidence_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal": self.signal.to_dict(),
            "affected_contexts": self.affected_contexts,
            "drained_contexts": self.drained_contexts,
            "halted_at": self.halted_at,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class HaltResult:
    """Returned by ``KillSwitchController.issue``."""

    signal_id: str
    halted: bool
    affected_contexts: List[str]
    drained_contexts: List[str]
    evidence_ref: str
    violations: List[str] = field(default_factory=list)


class ExecutionContext(Protocol):
    """An active execution context (loop or goal) that must respect the halt.

    Fail-closed contract: after ``on_halt`` the context MUST report
    ``is_halted() == True``. The controller audits this and raises
    ``HaltViolation`` if any context skips the halt.
    """

    context_id: str
    context_type: str  # "loop" | "goal"

    def on_halt(self, signal: HaltSignal) -> None:
        """Layer must set its internal halted flag. Fail-closed."""
        ...

    def is_halted(self) -> bool:
        """The context's own reported compliance state."""
        ...

    def drain(self) -> "DrainResult | None":
        """Gracefully drain in-flight work; return state to persist."""
        ...
