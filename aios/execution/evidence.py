"""Execution Evidence + Conformance (TASK-144, M20).

Standardizes execution evidence across the T135->T143 pipeline and runs a
fail-closed conformance check. Every evidence record carries a ``content_hash``
(T078) and a full provenance chain (T001 Rule 5). ``evidence_id`` is immutable
(T001 Rule 1). Fail-closed: unverified evidence is never promoted to PASS (T078).

Layering: ``execution`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from aios.execution._common import ExecutionError, _hash


class EvidenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


@dataclass
class ExecutionEvidence:
    """Standardized execution evidence record (T144)."""

    evidence_id: str
    pipeline_ref: str  # T135->T143
    content_hash: str
    producer: str  # runner/harness
    evidence_chain: List[str] = field(default_factory=list)
    integrity_verified: bool = False
    policy_ref: Optional[str] = None
    status: EvidenceStatus = EvidenceStatus.UNVERIFIED

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ExecutionError("evidence_id required (T001 Rule 1, immutable).")
        if not self.content_hash:
            raise ExecutionError("content_hash required (T078).")

    def promote(self) -> None:
        # Fail-closed: cannot promote unverified evidence to PASS (T078).
        if not self.integrity_verified:
            raise ExecutionError("Cannot promote unverified evidence to PASS (T078).")
        self.status = EvidenceStatus.VERIFIED


class ExecutionEvidenceRegistry:
    """Registry + conformance for execution evidence (T144)."""

    def __init__(self) -> None:
        self._evidence: Dict[str, ExecutionEvidence] = {}

    def record(self, ev: ExecutionEvidence) -> ExecutionEvidence:
        if ev.evidence_id in self._evidence:
            raise ExecutionError(f"Duplicate evidence_id '{ev.evidence_id}' (T001 Rule 1).")
        self._evidence[ev.evidence_id] = ev
        return ev

    def get(self, evidence_id: str) -> ExecutionEvidence:
        if evidence_id not in self._evidence:
            raise ExecutionError(f"Unknown evidence '{evidence_id}'.")
        return self._evidence[evidence_id]

    def conformance(self, evidence_id: str) -> dict:
        ev = self.get(evidence_id)
        return {
            "evidence_id": ev.evidence_id,
            "pipeline_ref": ev.pipeline_ref,
            "content_hash": ev.content_hash,
            "producer": ev.producer,
            "evidence_chain": list(ev.evidence_chain),
            "integrity_verified": ev.integrity_verified,
            "policy_ref": ev.policy_ref,
            "status": ev.status.value,
            "verdict": "PASS" if ev.status == EvidenceStatus.VERIFIED else "BLOCK",
        }
