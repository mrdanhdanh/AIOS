"""Autonomous Safety Controller (TASK-153, M21).

Sets the autonomy boundary (blast radius) for the coding loop and triggers the
kill switch (T068) on boundary violation, using Autonomy Safety T067. Built on
Context Refresh + Patch Chain T152 + Evidence T001. TASK-153 is a *safety
controller*, not a new loop.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.patch_chain import PatchChain


@dataclass
class SafetyDecision:
    """Immutable-by-id safety decision (T153)."""

    decision_id: str
    chain_ref: str
    boundary_status: str
    kill_switch: bool
    guardrail_ref: str
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise CodingLoopError("decision_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("SafetyDecision requires evidence_ref (T001 Rule 5).")


class AutonomousSafetyController:
    """Deterministic safety controller; fail-closed kill switch on violation (T153)."""

    def __init__(self, guardrail_ref: str = "gr-default") -> None:
        self._guardrail_ref = guardrail_ref
        self._decisions: Dict[str, SafetyDecision] = {}

    def evaluate(
        self,
        patch_chain: PatchChain,
        boundary_status: str = "within",
        evidence_ref: Optional[str] = None,
        decision_id: Optional[str] = None,
    ) -> SafetyDecision:
        # Fail-closed: safety requires a patch chain with provenance (T001 Rule 5).
        if patch_chain is None or not patch_chain.evidence_ref:
            raise CodingLoopError("Safety requires patch chain with provenance (T001 Rule 5).")
        # Fail-closed: boundary violation -> kill switch (T068).
        kill_switch = boundary_status != "within"
        ev = evidence_ref or patch_chain.evidence_ref
        did = decision_id or f"safe-{uuid.uuid4().hex[:12]}"
        if did in self._decisions:
            raise CodingLoopError(f"Duplicate decision_id '{did}' (T001 Rule 1).")
        dec = SafetyDecision(
            decision_id=did,
            chain_ref=patch_chain.chain_id,
            boundary_status=boundary_status,
            kill_switch=kill_switch,
            guardrail_ref=self._guardrail_ref,
            evidence_ref=ev,
        )
        self._decisions[did] = dec
        return dec

    def get(self, decision_id: str) -> SafetyDecision:
        if decision_id not in self._decisions:
            raise CodingLoopError(f"Unknown decision '{decision_id}'.")
        return self._decisions[decision_id]

    def provenance(self, decision_id: str) -> dict:
        dec = self.get(decision_id)
        payload = (
            f"{dec.decision_id}|{dec.chain_ref}|{dec.boundary_status}|"
            f"{dec.kill_switch}|{dec.guardrail_ref}|{dec.evidence_ref}"
        )
        return {
            "decision_id": dec.decision_id,
            "chain_ref": dec.chain_ref,
            "boundary_status": dec.boundary_status,
            "kill_switch": dec.kill_switch,
            "guardrail_ref": dec.guardrail_ref,
            "evidence_ref": dec.evidence_ref,
            "authority": dec.authority,
            "content_hash": _hash(payload),
        }
