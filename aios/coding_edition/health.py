"""TASK-213 — Coding Health Score (M26).

Compute a composite coding health score, converging Health Score (T213) and
Quality Dimensions (T187). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aios.coding_edition._common import CodingEditionError, _hash


@dataclass(frozen=True)
class HealthDimension:
    """A weighted health dimension (T213)."""

    name: str
    weight: float

    def __post_init__(self) -> None:
        if not self.name:
            raise CodingEditionError("dimension name is required.")
        if self.weight < 0.0 or self.weight > 1.0:
            raise CodingEditionError("weight must be in [0,1].")


@dataclass
class HealthReport:
    """An immutable-by-id health report (T213)."""

    report_id: str
    score: float
    dimensions: Dict[str, float]

    def __post_init__(self) -> None:
        if not self.report_id:
            raise CodingEditionError("report_id is required (T001 Rule 1, immutable).")
        if not 0.0 <= self.score <= 1.0:
            raise CodingEditionError("score must be in [0,1].")


class CodingHealthScore:
    """Deterministic coding health scorer (T213)."""

    def __init__(self, dimensions: Optional[List[HealthDimension]] = None) -> None:
        self._dims: List[HealthDimension] = list(dimensions or [HealthDimension("quality", 0.5), HealthDimension("reliability", 0.5)])

    def compute(self, scores: Dict[str, float]) -> HealthReport:
        """Compute weighted health score in [0,1] (fail-closed)."""
        total_w = sum(d.weight for d in self._dims)
        if total_w <= 0.0:
            raise CodingEditionError("total dimension weight must be > 0.")
        missing = [d.name for d in self._dims if d.name not in scores]
        if missing:
            raise CodingEditionError(f"missing dimension scores: {missing}")
        acc = 0.0
        for d in self._dims:
            v = scores[d.name]
            if not 0.0 <= v <= 1.0:
                raise CodingEditionError(f"dimension '{d.name}' score must be in [0,1].")
            acc += d.weight * v
        score = min(1.0, acc / total_w)
        return HealthReport(report_id=f"hlth-{uuid.uuid4().hex[:8]}", score=score, dimensions=dict(scores))

    def health_hash(self, report: HealthReport) -> str:
        payload = "|".join(f"{k}:{v}" for k, v in sorted(report.dimensions.items()))
        return _hash(f"{report.report_id}|{report.score:.4f}|{payload}")
