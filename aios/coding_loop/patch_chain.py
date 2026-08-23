"""Context Refresh + Patch Chain (TASK-152, M21).

Refreshes context (Context Optimizer T024) and chains patches (Workspace/
Snapshot T137) across loop iterations, after the verification gate (T151) PASS.
Built on Verification Gate T151 + Evidence T001. TASK-152 is *refresh + chain*,
not a new optimizer.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.verification_gate import VerifyStatus, VerificationResult


@dataclass
class PatchChain:
    """Immutable-by-id patch chain (T152)."""

    chain_id: str
    verification_ref: str
    context_ref: str
    patch_links: Tuple[str, ...]
    snapshot_ref: str
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.chain_id:
            raise CodingLoopError("chain_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("PatchChain requires evidence_ref (T001 Rule 5).")


class ContextRefreshPatchChain:
    """Deterministic context refresh + patch chain; fail-closed on mismatch (T152)."""

    def __init__(self) -> None:
        self._chains: Dict[str, PatchChain] = {}

    def refresh_context(self, state: str) -> str:
        """Deterministic context refresh: same state -> same refreshed context (T024)."""
        return f"ctx-{_hash(state)[:12]}"

    def refresh_and_chain(
        self,
        verification_result: VerificationResult,
        context_ref: str,
        snapshot_before: str,
        snapshot_after: str,
        patch_links: Optional[List[str]] = None,
        evidence_ref: Optional[str] = None,
        chain_id: Optional[str] = None,
    ) -> PatchChain:
        # Fail-closed: chain requires a verification result with provenance (T001 Rule 5).
        if verification_result is None or not verification_result.evidence_ref:
            raise CodingLoopError("Chain requires verification result with provenance (T001 Rule 5).")
        # Fail-closed: snapshot before/after must match (T137).
        if snapshot_before != snapshot_after:
            raise CodingLoopError("Snapshot before/after mismatch (T137, fail-closed).")
        # Fail-closed: only verified (PASS) output may be chained (T078).
        if verification_result.verification_result.value != VerifyStatus.PASS.value:
            raise CodingLoopError("Cannot chain unverified output (T078, fail-closed).")
        links = tuple(patch_links or [])
        ev = evidence_ref or verification_result.evidence_ref
        cid = chain_id or f"chain-{uuid.uuid4().hex[:12]}"
        if cid in self._chains:
            raise CodingLoopError(f"Duplicate chain_id '{cid}' (T001 Rule 1).")
        chain = PatchChain(
            chain_id=cid,
            verification_ref=verification_result.result_id,
            context_ref=context_ref,
            patch_links=links,
            snapshot_ref=snapshot_before,
            evidence_ref=ev,
        )
        self._chains[cid] = chain
        return chain

    def get(self, chain_id: str) -> PatchChain:
        if chain_id not in self._chains:
            raise CodingLoopError(f"Unknown chain '{chain_id}'.")
        return self._chains[chain_id]

    def provenance(self, chain_id: str) -> dict:
        ch = self.get(chain_id)
        payload = (
            f"{ch.chain_id}|{ch.verification_ref}|{ch.context_ref}|"
            f"{len(ch.patch_links)}|{ch.snapshot_ref}|{ch.evidence_ref}"
        )
        return {
            "chain_id": ch.chain_id,
            "verification_ref": ch.verification_ref,
            "context_ref": ch.context_ref,
            "patch_links": len(ch.patch_links),
            "snapshot_ref": ch.snapshot_ref,
            "evidence_ref": ch.evidence_ref,
            "authority": ch.authority,
            "content_hash": _hash(payload),
        }
