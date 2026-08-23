"""TASK-197 — Unified Coding Contract (M26).

Single, contract-driven definition of the AIOS 2.0 Coding Edition. Converges
the Coder Contract (T125), Coding Evaluation Contract (T185) and Evidence
contract (T001 Rule 5) into one immutable, capability-injected contract.

Pure and side-effect free: all I/O goes through Runtime/Capability
(ARCH-001..004). Provenance is recorded on every transition (T001 Rule 5).
Fail-closed: a missing mandatory field rejects construction. Deterministic:
same inputs -> same contract id.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

from aios.coding_edition._common import CodingEditionError, _hash


class CompletionState(str, Enum):
    """Coding Completion Contract chain (M26 overview)."""

    AUTHORIZED = "AUTHORIZED"
    EXECUTED = "EXECUTED"
    VERIFIED = "VERIFIED"
    RESILIENT = "RESILIENT"
    GOVERNED = "GOVERNED"
    EVALUATED = "EVALUATED"
    CERTIFIED = "CERTIFIED"


# Ordered completion chain; each state depends on the previous (acyclic).
COMPLETION_CHAIN: Tuple[CompletionState, ...] = (
    CompletionState.AUTHORIZED,
    CompletionState.EXECUTED,
    CompletionState.VERIFIED,
    CompletionState.RESILIENT,
    CompletionState.GOVERNED,
    CompletionState.EVALUATED,
    CompletionState.CERTIFIED,
)


@dataclass(frozen=True)
class CodingEditionContract:
    """Unified, I/O-free coding contract (T197).

    The agent never performs I/O directly; it only observes capabilities that
    are injected by the orchestrator/runtime (T013 / ARCH-004).
    """

    contract_id: str
    version: str = "2.0"
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    completion_states: Tuple[CompletionState, ...] = field(default_factory=lambda: COMPLETION_CHAIN)
    policy_ref: Optional[str] = None
    evidence_ref: Optional[str] = None
    io_free: bool = True

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise CodingEditionError("contract_id is required (T001 Rule 1, immutable).")
        if not self.version:
            raise CodingEditionError("version is required.")
        if not self.io_free:
            raise CodingEditionError("coding edition contract must be I/O-free (ARCH-001..004).")
        # Completion chain must be a prefix-ordered subsequence of COMPLETION_CHAIN.
        full = list(COMPLETION_CHAIN)
        idx = 0
        for state in self.completion_states:
            if state not in COMPLETION_CHAIN:
                raise CodingEditionError(f"unknown completion state: {state}")
            pos = full.index(state)
            if pos < idx:
                raise CodingEditionError("completion_states must preserve chain order.")
            idx = pos

    @property
    def contract_hash(self) -> str:
        """Deterministic, content-addressed identity (no clock)."""
        payload = "|".join(
            [
                self.contract_id,
                self.version,
                ",".join(self.capabilities),
                ",".join(s.value for s in self.completion_states),
                self.policy_ref or "",
                self.evidence_ref or "",
            ]
        )
        return _hash(payload)

    def verify_completion(self, reached: Tuple[CompletionState, ...]) -> bool:
        """Fail-closed check that ``reached`` is a valid prefix of the chain."""
        if len(reached) > len(self.completion_states):
            return False
        for expected, actual in zip(self.completion_states, reached):
            if expected != actual:
                return False
        return True
