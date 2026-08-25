"""Coder Agent Contract + State Machine (TASK-125, M19).

Defines the I/O-free, capability-injected coder agent contract and the
coding-task lifecycle state machine. Pure and side-effect free: all I/O goes
through Runtime/Capability (ARCH-001..004). Provenance is recorded on every
transition (T001 Rule 5). Fail-closed: a missing mandatory artifact rejects the
transition (T001 Rule 6). Deterministic: same state + same artifacts -> same
transition result.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set


class CodingTaskState(str, Enum):
    """Coding-task lifecycle states (T125, based on T001 Rule 6)."""

    PLANNED = "PLANNED"
    CODING = "CODING"
    REVIEWING = "REVIEWING"
    PATCHING = "PATCHING"
    DONE = "DONE"


# Valid forward transitions (acyclic; REVIEWING<->PATCHING loop allowed).
_CODING_TRANSITIONS: Dict[CodingTaskState, List[CodingTaskState]] = {
    CodingTaskState.PLANNED: [CodingTaskState.CODING],
    CodingTaskState.CODING: [CodingTaskState.REVIEWING, CodingTaskState.PATCHING],
    CodingTaskState.REVIEWING: [CodingTaskState.PATCHING, CodingTaskState.DONE],
    CodingTaskState.PATCHING: [CodingTaskState.REVIEWING, CodingTaskState.DONE],
    CodingTaskState.DONE: [],
}

# Mandatory artifacts required to enter each coding state (fail-closed, T001).
_CODING_ARTIFACTS: Dict[CodingTaskState, List[str]] = {
    CodingTaskState.PLANNED: [],
    CodingTaskState.CODING: ["plan"],
    CodingTaskState.REVIEWING: ["generated_code"],
    CodingTaskState.PATCHING: ["review_result"],
    CodingTaskState.DONE: ["final_artifact", "evidence"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CoderAgentError(Exception):
    """Raised on contract or state-machine violations (fail-closed)."""


@dataclass(frozen=True)
class CoderAgentContract:
    """I/O-free, capability-injected coder agent contract (T125).

    The agent never performs I/O directly; it only observes capabilities that
    are injected by the orchestrator/runtime (T013 / ARCH-004).
    """

    agent_id: str
    capabilities: tuple = field(default_factory=tuple)
    states: tuple = field(default_factory=lambda: tuple(CodingTaskState))
    io_free: bool = True
    policy_ref: Optional[str] = None
    evidence_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise CoderAgentError("agent_id is required (T001 Rule 1, immutable).")
        if not self.io_free:
            raise CoderAgentError("coder agent must be I/O-free (ARCH-001..004).")

    def can_inject(self, capability: str) -> bool:
        """True when the capability may be injected into this agent."""
        return capability in self.capabilities


class CoderCapabilityResolver:
    """TASK-230: wire a :class:`CoderAgentContract` to a ``CapabilityRegistry``.

    The resolver is capability-injected (the registry is passed in, never
    imported directly by the agent). It resolves a capability name against BOTH
    the agent's declared ``capabilities`` and the live registry, failing
    closed when either check fails (no guessing, no direct I/O).
    """

    def __init__(self, contract: CoderAgentContract, registry: "CapabilityRegistry") -> None:
        self._contract = contract
        self._registry = registry

    def resolve(self, capability: str) -> List[str]:
        """Return ordered tool_ids for *capability* (fail-closed).

        Raises :class:`CoderAgentError` when the capability is not declared on
        the contract or not present in the registry.
        """
        if not self._contract.can_inject(capability):
            raise CoderAgentError(
                f"capability {capability!r} not declared on contract "
                f"{self._contract.agent_id!r} (ARCH-004: inject only)"
            )
        if capability not in self._registry:
            raise CoderAgentError(
                f"capability {capability!r} not found in CapabilityRegistry"
            )
        return self._registry.resolve(capability)

    def is_resolvable(self, capability: str) -> bool:
        """Non-raising variant of :meth:`resolve`."""
        try:
            self.resolve(capability)
            return True
        except CoderAgentError:
            return False


@dataclass
class TransitionRecord:
    """Provenance record for a single state transition (T001 Rule 5)."""

    transition_id: str
    from_state: CodingTaskState
    to_state: CodingTaskState
    task_id: str
    run_id: str
    evidence_id: str
    content_hash: str
    timestamp: str
    policy_ok: bool


class CoderAgentStateMachine:
    """Coding-task lifecycle state machine (T125)."""

    def __init__(self, contract: CoderAgentContract) -> None:
        self._contract = contract
        self._states: Dict[str, CodingTaskState] = {}
        self._history: Dict[str, List[TransitionRecord]] = {}

    # ------------------------------------------------------------------ #
    # init / current
    # ------------------------------------------------------------------ #
    def init(
        self, task_id: str, state: CodingTaskState = CodingTaskState.PLANNED
    ) -> CodingTaskState:
        if state not in _CODING_TRANSITIONS:
            raise CoderAgentError(f"Unknown state {state}.")
        self._states[task_id] = state
        return state

    def current(self, task_id: str) -> CodingTaskState:
        if task_id not in self._states:
            raise CoderAgentError(f"Task '{task_id}' not initialized.")
        return self._states[task_id]

    # ------------------------------------------------------------------ #
    # transition validation
    # ------------------------------------------------------------------ #
    def can_transition(self, task_id: str, to_state: CodingTaskState) -> bool:
        try:
            self._validate(task_id, to_state, set())
            return True
        except CoderAgentError:
            return False

    def _validate(
        self, task_id: str, to_state: CodingTaskState, artifacts: Set[str]
    ) -> None:
        if to_state not in _CODING_TRANSITIONS:
            raise CoderAgentError(f"Unknown state {to_state}.")
        current = self._states.get(task_id)
        if current is None:
            raise CoderAgentError(f"Task '{task_id}' not initialized.")
        if to_state == current:
            return
        if to_state not in _CODING_TRANSITIONS[current]:
            raise CoderAgentError(f"Illegal transition {current} -> {to_state}.")
        required = _CODING_ARTIFACTS.get(to_state, [])
        missing = [a for a in required if a not in artifacts]
        if missing:
            raise CoderAgentError(
                f"Missing mandatory artifacts for {to_state}: {missing}."
            )

    def transition(
        self,
        task_id: str,
        to_state: CodingTaskState,
        artifacts: Set[str],
        run_id: str = "",
        policy_ok: bool = True,
    ) -> CodingTaskState:
        """Transition ``task_id`` to ``to_state``.

        Fail-closed: a rejected policy or a missing mandatory artifact rejects
        the transition (T001 Rule 6 / T113). Every successful transition emits a
        provenance record (T001 Rule 5).
        """
        if not policy_ok:
            raise CoderAgentError("Policy rejected transition (T113).")
        self._validate(task_id, to_state, set(artifacts))
        from_state = self._states[task_id]
        evidence_id = f"ev-{uuid.uuid4().hex[:12]}"
        content = f"{task_id}:{from_state.value}->{to_state.value}:{sorted(artifacts)}"
        rec = TransitionRecord(
            transition_id=f"tr-{uuid.uuid4().hex[:12]}",
            from_state=from_state,
            to_state=to_state,
            task_id=task_id,
            run_id=run_id or f"run-{uuid.uuid4().hex[:12]}",
            evidence_id=evidence_id,
            content_hash=_hash(content),
            timestamp=_now(),
            policy_ok=policy_ok,
        )
        self._states[task_id] = to_state
        self._history.setdefault(task_id, []).append(rec)
        return to_state

    # ------------------------------------------------------------------ #
    # provenance
    # ------------------------------------------------------------------ #
    def history(self, task_id: str) -> List[TransitionRecord]:
        return list(self._history.get(task_id, []))

    def provenance_chain(self, task_id: str) -> List[dict]:
        """Return the full provenance chain for a task (T001 Rule 5)."""
        return [
            {
                "evidence_id": r.evidence_id,
                "task_id": r.task_id,
                "run_id": r.run_id,
                "from_state": r.from_state.value,
                "to_state": r.to_state.value,
                "content_hash": r.content_hash,
                "timestamp": r.timestamp,
            }
            for r in self._history.get(task_id, [])
        ]
