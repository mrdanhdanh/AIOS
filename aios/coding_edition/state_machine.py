"""TASK-198 — Coding State Machine (M26).

Deterministic, fail-closed state machine driving the Coding Completion
Contract chain (AUTHORIZED -> EXECUTED -> VERIFIED -> RESILIENT -> GOVERNED ->
EVALUATED -> CERTIFIED). Built on Coder State Machine (T125) + Coding Loop
(T145) + Lifecycle (T001 Rule 6).

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash, _now
from aios.coding_edition.contract import COMPLETION_CHAIN, CompletionState


class CodingEditionState(str, Enum):
    """Coding edition lifecycle states (T198)."""

    IDLE = "IDLE"
    AUTHORIZED = "AUTHORIZED"
    EXECUTED = "EXECUTED"
    VERIFIED = "VERIFIED"
    RESILIENT = "RESILIENT"
    GOVERNED = "GOVERNED"
    EVALUATED = "EVALUATED"
    CERTIFIED = "CERTIFIED"
    FAILED = "FAILED"


# Forward transitions (acyclic; VERIFIED<->RESILIENT loop allowed for repair).
_TRANSITIONS: Dict[CodingEditionState, List[CodingEditionState]] = {
    CodingEditionState.IDLE: [CodingEditionState.AUTHORIZED],
    CodingEditionState.AUTHORIZED: [CodingEditionState.EXECUTED, CodingEditionState.FAILED],
    CodingEditionState.EXECUTED: [CodingEditionState.VERIFIED, CodingEditionState.FAILED],
    CodingEditionState.VERIFIED: [CodingEditionState.RESILIENT, CodingEditionState.EXECUTED],
    CodingEditionState.RESILIENT: [CodingEditionState.GOVERNED, CodingEditionState.VERIFIED],
    CodingEditionState.GOVERNED: [CodingEditionState.EVALUATED, CodingEditionState.FAILED],
    CodingEditionState.EVALUATED: [CodingEditionState.CERTIFIED, CodingEditionState.FAILED],
    CodingEditionState.CERTIFIED: [],
    CodingEditionState.FAILED: [CodingEditionState.AUTHORIZED],
}

# Mandatory artifacts required to enter each state (fail-closed, T001).
_ARTIFACTS: Dict[CodingEditionState, List[str]] = {
    CodingEditionState.IDLE: [],
    CodingEditionState.AUTHORIZED: ["authorization"],
    CodingEditionState.EXECUTED: ["generated_code"],
    CodingEditionState.VERIFIED: ["verification_report"],
    CodingEditionState.RESILIENT: ["recovery_report"],
    CodingEditionState.GOVERNED: ["governance_evidence"],
    CodingEditionState.EVALUATED: ["evaluation_report"],
    CodingEditionState.CERTIFIED: ["certificate"],
    CodingEditionState.FAILED: [],
}


@dataclass
class TransitionRecord:
    """A single recorded transition (provenance, T001 Rule 5)."""

    from_state: CodingEditionState
    to_state: CodingEditionState
    artifact: str
    evidence_ref: str
    at: str = field(default_factory=_now)


class CodingEditionStateMachine:
    """Deterministic, fail-closed coding edition state machine (T198)."""

    def __init__(self, run_id: Optional[str] = None, evidence_ref: Optional[str] = None) -> None:
        self._run_id = run_id or f"ce-{uuid.uuid4().hex[:12]}"
        self._state = CodingEditionState.IDLE
        self._evidence_ref = evidence_ref or self._run_id
        self._history: List[TransitionRecord] = []

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def state(self) -> CodingEditionState:
        return self._state

    @property
    def history(self) -> List[TransitionRecord]:
        return list(self._history)

    def can_transition(self, to: CodingEditionState) -> bool:
        return to in _TRANSITIONS.get(self._state, [])

    def transition(self, to: CodingEditionState, artifact: str, evidence_ref: Optional[str] = None) -> TransitionRecord:
        """Transition to ``to`` if allowed and artifacts are present (fail-closed)."""
        if not self.can_transition(to):
            raise CodingEditionError(
                f"illegal transition {self._state.value} -> {to.value}",
                detail="not in allowed forward transitions",
            )
        required = _ARTIFACTS.get(to, [])
        if artifact not in required:
            raise CodingEditionError(
                f"missing mandatory artifact for {to.value}",
                detail=f"expected one of {required}, got '{artifact}'",
            )
        rec = TransitionRecord(
            from_state=self._state,
            to_state=to,
            artifact=artifact,
            evidence_ref=evidence_ref or self._evidence_ref,
        )
        self._history.append(rec)
        self._state = to
        return rec

    def provenance_chain(self) -> str:
        """Content-addressed provenance of the full transition history."""
        payload = "|".join(
            f"{r.from_state.value}->{r.to_state.value}:{r.artifact}:{r.evidence_ref}"
            for r in self._history
        )
        return _hash(payload)

    def completion_progress(self) -> float:
        """Fraction of the COMPLETION_CHAIN reached (0.0..1.0)."""
        reached = [s for s in COMPLETION_CHAIN if s.value == self._state.value]
        if self._state == CodingEditionState.CERTIFIED:
            return 1.0
        if not reached:
            return 0.0
        return (COMPLETION_CHAIN.index(reached[0]) + 1) / len(COMPLETION_CHAIN)
