"""TASK-206 — Coding Session (M26).

Coding session lifecycle, converging Session/State (T125/T145). Deterministic,
fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash, _now


class SessionState(str, Enum):
    """Coding session states (T206)."""

    OPEN = "OPEN"
    CODING = "CODING"
    REVIEWING = "REVIEWING"
    CLOSED = "CLOSED"


@dataclass
class SessionStep:
    """A recorded step within a coding session (T206)."""

    step_id: str
    artifact: str
    at: str = field(default_factory=_now)


class CodingSession:
    """Deterministic coding session (T206)."""

    def __init__(self, session_id: Optional[str] = None, goal: str = "") -> None:
        self._session_id = session_id or f"sess-{uuid.uuid4().hex[:12]}"
        if not goal:
            raise CodingEditionError("session goal is required.")
        self._goal = goal
        self._state = SessionState.OPEN
        self._steps: List[SessionStep] = []
        self._artifacts: Dict[str, str] = {}

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def steps(self) -> List[SessionStep]:
        return list(self._steps)

    def start(self) -> None:
        if self._state != SessionState.OPEN:
            raise CodingEditionError(f"cannot start from {self._state.value}")
        self._state = SessionState.CODING

    def commit_step(self, artifact: str, content_hash: str) -> SessionStep:
        """Record a committed step with provenance (fail-closed)."""
        if self._state not in (SessionState.CODING, SessionState.REVIEWING):
            raise CodingEditionError(f"cannot commit in {self._state.value}")
        if not content_hash:
            raise CodingEditionError("content_hash is required (provenance).")
        step = SessionStep(step_id=f"st-{uuid.uuid4().hex[:8]}", artifact=artifact)
        self._steps.append(step)
        self._artifacts[artifact] = content_hash
        return step

    def review(self) -> None:
        if self._state != SessionState.CODING:
            raise CodingEditionError(f"cannot review from {self._state.value}")
        self._state = SessionState.REVIEWING

    def close(self) -> None:
        if not self._steps:
            raise CodingEditionError("cannot close an empty session.")
        self._state = SessionState.CLOSED

    def session_hash(self) -> str:
        payload = "|".join(f"{s.artifact}:{self._artifacts.get(s.artifact, '')}" for s in self._steps)
        return _hash(f"{self._session_id}|{self._goal}|{payload}")
