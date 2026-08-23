"""Execution Observation (TASK-146, M21).

Observation layer that captures the execution trace/event stream during the
coding loop (T145) to feed failure classification (T147). Built on Execution
Contract T135 + Output/Artifact Collector T141 + Evidence T001. TASK-146 is an
*observation* layer, not a new classifier.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple

from aios.coding_loop._common import CodingLoopError, _hash, _now, redact_secret


class ObservationStatus(str, Enum):
    """Observation lifecycle states (T146)."""

    CAPTURED = "CAPTURED"
    REJECTED = "REJECTED"


@dataclass
class Observation:
    """Immutable-by-id execution observation (T146)."""

    observation_id: str
    loop_ref: str
    execution_ref: str
    trace: Tuple[str, ...]
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.observation_id:
            raise CodingLoopError("observation_id required (T001 Rule 1, immutable).")
        # Fail-closed: observation without provenance is never promoted (T001 Rule 5).
        if not self.evidence_ref:
            raise CodingLoopError("Observation requires evidence_ref (T001 Rule 5, fail-closed).")


class ExecutionObservation:
    """Captures execution traces with provenance; deterministic + fail-closed (T146)."""

    def __init__(self) -> None:
        self._observations: Dict[str, Observation] = {}

    def capture(
        self,
        execution_ref: str,
        loop_ref: str,
        trace: Tuple[str, ...],
        evidence_ref: Optional[str] = None,
        observation_id: Optional[str] = None,
    ) -> Observation:
        # Fail-closed: provenance + loop linkage required.
        if not execution_ref or not loop_ref:
            raise CodingLoopError("execution_ref and loop_ref required (T145/T135).")
        if evidence_ref is None:
            raise CodingLoopError("Observation requires evidence_ref (T001 Rule 5).")
        oid = observation_id or f"obs-{uuid.uuid4().hex[:12]}"
        if oid in self._observations:
            raise CodingLoopError(f"Duplicate observation_id '{oid}' (T001 Rule 1).")
        # Deterministic: same execution -> same (redacted) trace. Secrets redacted (T040/T113).
        redacted = tuple(redact_secret(t) for t in (trace or ()))
        obs = Observation(
            observation_id=oid,
            loop_ref=loop_ref,
            execution_ref=execution_ref,
            trace=redacted,
            evidence_ref=evidence_ref,
        )
        self._observations[oid] = obs
        return obs

    def get(self, observation_id: str) -> Observation:
        if observation_id not in self._observations:
            raise CodingLoopError(f"Unknown observation '{observation_id}'.")
        return self._observations[observation_id]

    def provenance(self, observation_id: str) -> dict:
        obs = self.get(observation_id)
        payload = (
            f"{obs.observation_id}|{obs.execution_ref}|{obs.loop_ref}|"
            f"{len(obs.trace)}|{obs.evidence_ref}"
        )
        return {
            "observation_id": obs.observation_id,
            "execution_ref": obs.execution_ref,
            "loop_ref": obs.loop_ref,
            "trace_len": len(obs.trace),
            "evidence_ref": obs.evidence_ref,
            "authority": obs.authority,
            "content_hash": _hash(payload),
        }
