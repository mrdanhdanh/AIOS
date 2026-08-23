"""Coding Loop State Machine (TASK-145, M21).

Controls the autonomous coding loop (observe -> classify -> diagnose -> repair ->
verify -> refresh -> safety) through a deterministic, fail-closed state machine.
TASK-145 is the *control* state machine, not a new execution substrate (built on
Autonomous Loop T053 + Goal Engine T050 + Evidence T001 Rule 5/6 + Lifecycle
T001 Rule 6).

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now


class CodingLoopState(str, Enum):
    """Coding loop states (T145)."""

    OBSERVING = "OBSERVING"
    CLASSIFYING = "CLASSIFYING"
    DIAGNOSING = "DIAGNOSING"
    REPAIRING = "REPAIRING"
    VERIFYING = "VERIFYING"
    REFRESHING = "REFRESHING"
    SAFETY = "SAFETY"
    DONE = "DONE"


# Deterministic transition map: same state -> same next state (T001 Rule 6).
TRANSITIONS: Dict[CodingLoopState, CodingLoopState] = {
    CodingLoopState.OBSERVING: CodingLoopState.CLASSIFYING,
    CodingLoopState.CLASSIFYING: CodingLoopState.DIAGNOSING,
    CodingLoopState.DIAGNOSING: CodingLoopState.REPAIRING,
    CodingLoopState.REPAIRING: CodingLoopState.VERIFYING,
    CodingLoopState.VERIFYING: CodingLoopState.REFRESHING,
    CodingLoopState.REFRESHING: CodingLoopState.SAFETY,
    CodingLoopState.SAFETY: CodingLoopState.DONE,
}


@dataclass
class CodingLoopRecord:
    """Immutable-by-id coding loop record (T145)."""

    loop_id: str
    current_state: CodingLoopState
    evidence_ref: Optional[str] = None
    policy_ref: Optional[str] = None
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.loop_id:
            raise CodingLoopError("loop_id required (T001 Rule 1, immutable).")


@dataclass
class TransitionEvent:
    """A single recorded transition (provenance, T001 Rule 5)."""

    from_state: CodingLoopState
    to_state: CodingLoopState
    artifact: str
    evidence_ref: str
    policy_ref: Optional[str]
    at: str = field(default_factory=_now)


class CodingLoopStateMachine:
    """Deterministic, fail-closed coding loop state machine (T145)."""

    def __init__(self, loop_id: Optional[str] = None, policy_ref: Optional[str] = None) -> None:
        lid = loop_id or f"loop-{uuid.uuid4().hex[:12]}"
        self._record = CodingLoopRecord(
            loop_id=lid,
            current_state=CodingLoopState.OBSERVING,
            policy_ref=policy_ref,
            evidence_ref=f"ev-{uuid.uuid4().hex[:12]}",
        )
        self._history: List[TransitionEvent] = []

    @property
    def loop_id(self) -> str:
        return self._record.loop_id

    @property
    def current_state(self) -> CodingLoopState:
        return self._record.current_state

    @property
    def transition_history(self) -> List[TransitionEvent]:
        return list(self._history)

    def next_state(self, current: Optional[CodingLoopState] = None) -> Optional[CodingLoopState]:
        """Deterministic next state for a given state (same input -> same output)."""
        st = current or self._record.current_state
        return TRANSITIONS.get(st)

    def transition(
        self,
        artifact: str,
        policy_ref: Optional[str] = None,
        evidence_ref: Optional[str] = None,
    ) -> CodingLoopState:
        # Fail-closed: every transition requires an artifact (T001 Rule 6).
        if not artifact:
            raise CodingLoopError("Transition requires artifact (T001 Rule 6, fail-closed).")
        # Fail-closed: every transition must pass through a policy boundary (T113).
        if policy_ref is None and self._record.policy_ref is None:
            raise CodingLoopError("Transition requires policy_ref (T113).")
        cur = self._record.current_state
        nxt = self.next_state(cur)
        if nxt is None:
            raise CodingLoopError(f"No transition defined from {cur.value}.")
        ev = evidence_ref or f"ev-{uuid.uuid4().hex[:12]}"
        self._history.append(
            TransitionEvent(
                from_state=cur,
                to_state=nxt,
                artifact=artifact,
                evidence_ref=ev,
                policy_ref=policy_ref or self._record.policy_ref,
                at=_now(),
            )
        )
        self._record.current_state = nxt
        self._record.evidence_ref = ev
        return nxt

    def provenance(self) -> dict:
        rec = self._record
        payload = f"{rec.loop_id}|{rec.current_state.value}|{rec.policy_ref}|{len(self._history)}"
        return {
            "loop_id": rec.loop_id,
            "current_state": rec.current_state.value,
            "policy_ref": rec.policy_ref,
            "authority": rec.authority,
            "history_len": len(self._history),
            "content_hash": _hash(payload),
        }
