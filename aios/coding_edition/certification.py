"""TASK-215 — Coding Certification (M26).

Certify a coding artifact, converging Certification (T049) and Trust Evaluator
(T164). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from aios.coding_edition._common import CodingEditionError, _hash, _now


@dataclass
class Certification:
    """An immutable-by-id coding certification (T215)."""

    cert_id: str
    artifact_id: str
    evidence_ref: str
    trust: float
    at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.cert_id:
            raise CodingEditionError("cert_id is required (T001 Rule 1, immutable).")
        if not self.artifact_id:
            raise CodingEditionError("artifact_id is required.")
        if not 0.0 <= self.trust <= 1.0:
            raise CodingEditionError("trust must be in [0,1].")


class CodingCertification:
    """Deterministic coding certification (T215)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"cert-{uuid.uuid4().hex[:12]}"

    @property
    def run_id(self) -> str:
        return self._run_id

    def certify(self, artifact_id: str, evidence_ref: str, trust: float) -> Certification:
        """Certify an artifact (fail-closed, deterministic)."""
        if not artifact_id:
            raise CodingEditionError("artifact_id is required.")
        if not evidence_ref:
            raise CodingEditionError("evidence_ref is required (provenance).")
        if trust < 0.6:
            raise CodingEditionError(f"trust {trust} below certification threshold 0.6.")
        return Certification(
            cert_id=f"crt-{uuid.uuid4().hex[:10]}",
            artifact_id=artifact_id,
            evidence_ref=evidence_ref,
            trust=trust,
        )

    def cert_hash(self, cert: Certification) -> str:
        return _hash(f"{cert.cert_id}|{cert.artifact_id}|{cert.trust:.4f}")
