"""Failure Classification (TASK-147, M21).

Classifies a failure from an observation (T146) using a closed taxonomy,
deterministically. Built on Execution Observation T146 + Execution Contract T135
+ Evidence T001. TASK-147 is a *classifier*, not a new diagnostic agent.

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.observation import Observation


class FailureTaxonomy(str, Enum):
    """Closed failure taxonomy (T147). No class outside this set is produced."""

    SYNTAX = "SYNTAX"
    RUNTIME = "RUNTIME"
    LOGIC = "LOGIC"
    TIMEOUT = "TIMEOUT"
    RESOURCE = "RESOURCE"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


# Confidence below this threshold is treated as UNKNOWN (not promoted, T078).
CONFIDENCE_THRESHOLD = 0.5


@dataclass
class FailureClass:
    """Immutable-by-id failure classification (T147)."""

    class_id: str
    observation_ref: str
    taxonomy_label: str
    confidence: float
    evidence_ref: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.class_id:
            raise CodingLoopError("class_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("FailureClass requires evidence_ref (T001 Rule 5).")
        if not (0.0 <= self.confidence <= 1.0):
            raise CodingLoopError("confidence must be in [0,1].")


class FailureClassifier:
    """Deterministic failure classifier with a closed taxonomy (T147)."""

    def __init__(self) -> None:
        self._classes: Dict[str, FailureClass] = {}

    def classify(
        self,
        observation: Observation,
        evidence_ref: Optional[str] = None,
        class_id: Optional[str] = None,
    ) -> FailureClass:
        # Fail-closed: classification requires an observation with provenance (T001 Rule 5).
        if observation is None or not observation.evidence_ref:
            raise CodingLoopError("Classification requires observation with provenance (T001 Rule 5).")
        label, confidence = self._classify_trace(observation.trace)
        # Low confidence -> UNKNOWN (never promoted to PASS, T078).
        if confidence < CONFIDENCE_THRESHOLD:
            label = FailureTaxonomy.UNKNOWN.value
        ev = evidence_ref or observation.evidence_ref
        cid = class_id or f"fc-{uuid.uuid4().hex[:12]}"
        if cid in self._classes:
            raise CodingLoopError(f"Duplicate class_id '{cid}' (T001 Rule 1).")
        fc = FailureClass(
            class_id=cid,
            observation_ref=observation.observation_id,
            taxonomy_label=label,
            confidence=confidence,
            evidence_ref=ev,
        )
        self._classes[cid] = fc
        return fc

    def _classify_trace(self, trace: Tuple[str, ...]) -> Tuple[str, float]:
        """Deterministic mapping from trace text to (label, confidence)."""
        text = " ".join(trace).lower()
        if "syntaxerror" in text or "syntax error" in text:
            return (FailureTaxonomy.SYNTAX.value, 0.9)
        if "timeout" in text or "timed out" in text:
            return (FailureTaxonomy.TIMEOUT.value, 0.85)
        if "memoryerror" in text or "out of memory" in text:
            return (FailureTaxonomy.RESOURCE.value, 0.85)
        if "connection" in text or "network" in text or "unreachable" in text:
            return (FailureTaxonomy.NETWORK.value, 0.8)
        if "exception" in text or "traceback" in text or "error" in text:
            return (FailureTaxonomy.RUNTIME.value, 0.7)
        if "assert" in text or "expected" in text:
            return (FailureTaxonomy.LOGIC.value, 0.7)
        return (FailureTaxonomy.UNKNOWN.value, 0.1)

    def is_promotable(self, failure_class: FailureClass) -> bool:
        """UNKNOWN (low confidence) is never promoted to PASS (T078)."""
        return (
            failure_class.taxonomy_label != FailureTaxonomy.UNKNOWN.value
            and failure_class.confidence >= CONFIDENCE_THRESHOLD
        )

    def get(self, class_id: str) -> FailureClass:
        if class_id not in self._classes:
            raise CodingLoopError(f"Unknown class '{class_id}'.")
        return self._classes[class_id]

    def provenance(self, class_id: str) -> dict:
        fc = self.get(class_id)
        payload = (
            f"{fc.class_id}|{fc.observation_ref}|{fc.taxonomy_label}|"
            f"{fc.confidence}|{fc.evidence_ref}"
        )
        return {
            "class_id": fc.class_id,
            "observation_ref": fc.observation_ref,
            "taxonomy_label": fc.taxonomy_label,
            "confidence": fc.confidence,
            "evidence_ref": fc.evidence_ref,
            "authority": fc.authority,
            "content_hash": _hash(payload),
        }
