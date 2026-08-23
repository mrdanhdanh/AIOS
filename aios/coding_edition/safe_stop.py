"""TASK-203 — Safe Stop / Resume (M26).

Safe stop / resume for coding runs, converging SAFE-STOP (T102) and Kill
Switch (T068). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash, _now


class StopState(str, Enum):
    """Safe-stop lifecycle (T203)."""

    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RESUMED = "RESUMED"
    TERMINATED = "TERMINATED"


@dataclass
class Checkpoint:
    """An immutable-by-id safe-stop checkpoint (T203)."""

    checkpoint_id: str
    state: str
    at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.checkpoint_id:
            raise CodingEditionError("checkpoint_id is required (T001 Rule 1, immutable).")
        if not self.state:
            raise CodingEditionError("checkpoint state is required.")


class SafeStopController:
    """Deterministic safe-stop / resume controller (T203)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"ss-{uuid.uuid4().hex[:12]}"
        self._state = StopState.RUNNING
        self._checkpoints: List[Checkpoint] = []

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def state(self) -> StopState:
        return self._state

    @property
    def checkpoints(self) -> List[Checkpoint]:
        return list(self._checkpoints)

    def pause(self, snapshot: str) -> Checkpoint:
        """Persist a checkpoint and pause (fail-closed)."""
        if self._state not in (StopState.RUNNING, StopState.RESUMED):
            raise CodingEditionError(f"cannot pause from {self._state.value}")
        cp = Checkpoint(checkpoint_id=f"cp-{uuid.uuid4().hex[:8]}", state=snapshot)
        self._checkpoints.append(cp)
        self._state = StopState.PAUSED
        return cp

    def resume(self) -> None:
        """Resume from a paused state (fail-closed)."""
        if self._state != StopState.PAUSED:
            raise CodingEditionError(f"cannot resume from {self._state.value}")
        self._state = StopState.RESUMED

    def terminate(self) -> None:
        self._state = StopState.TERMINATED

    def latest_checkpoint(self) -> Optional[Checkpoint]:
        return self._checkpoints[-1] if self._checkpoints else None

    def checkpoint_hash(self) -> str:
        payload = "|".join(f"{c.checkpoint_id}:{c.state}" for c in self._checkpoints)
        return _hash(f"{self._run_id}|{payload}")
