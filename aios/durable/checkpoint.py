"""Durable execution checkpoint model (TASK-066).

Defines the :class:`Checkpoint` dataclass -- the durable, provenance-bearing
unit of execution state. This module depends only on the stdlib; the
``state_hash`` is normally derived from the runtime state store (T065) via
:mod:`aios.durable.integration`.

Layering: ``durable`` is a runtime-level durability concern; it imports no
peer packages directly (integration lives in :mod:`aios.durable.integration`).
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Checkpoint:
    """A durable, verified-or-not execution checkpoint (spec §2 Durability Contract).

    Canonical fields (per T066 spec):
      - execution_id: owning execution.
      - step_id: step this checkpoint bounds.
      - state_hash: integrity hash of the execution state snapshot.
      - verified: only verified checkpoints may be resumed (fail-closed).
      - created_at: ISO-8601 UTC timestamp.
      - evidence_ref: provenance reference (evidence id / run id).

    ``checkpoint_id`` is an additive stable identifier used for storage keying
    and deterministic tie-breaking; it is not part of the canonical contract.
    """

    execution_id: str
    step_id: str
    state_hash: str
    verified: bool
    created_at: str
    evidence_ref: str
    checkpoint_id: str = field(default_factory=lambda: f"dcp-{uuid.uuid4().hex[:12]}")

    @property
    def content_hash(self) -> str:
        """Deterministic integrity hash of the checkpoint contents."""
        payload = json.dumps(
            {
                "checkpoint_id": self.checkpoint_id,
                "execution_id": self.execution_id,
                "step_id": self.step_id,
                "state_hash": self.state_hash,
                "verified": self.verified,
                "created_at": self.created_at,
                "evidence_ref": self.evidence_ref,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "execution_id": self.execution_id,
            "step_id": self.step_id,
            "state_hash": self.state_hash,
            "verified": self.verified,
            "created_at": self.created_at,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        return cls(
            checkpoint_id=data.get("checkpoint_id", f"dcp-{uuid.uuid4().hex[:12]}"),
            execution_id=data["execution_id"],
            step_id=data["step_id"],
            state_hash=data["state_hash"],
            verified=bool(data["verified"]),
            created_at=data["created_at"],
            evidence_ref=data.get("evidence_ref", ""),
        )
