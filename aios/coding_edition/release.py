"""TASK-214 — Release Gate (M26).

Gate a release candidate, converging Release Gate (T180) and Quality Gate
(T175). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from aios.coding_edition._common import CodingEditionError, _hash


class ReleaseVerdict(str, Enum):
    """Release outcome (T214)."""

    GO = "GO"
    NOGO = "NOGO"
    UNKNOWN = "UNKNOWN"


@dataclass
class ReleaseCandidate:
    """A release candidate under gate evaluation (T214)."""

    candidate_id: str
    tests_passed: bool = False
    coverage: float = 0.0
    certified: bool = False
    evidence_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise CodingEditionError("candidate_id is required (T001 Rule 1, immutable).")
        if not 0.0 <= self.coverage <= 1.0:
            raise CodingEditionError("coverage must be in [0,1].")


class ReleaseGate:
    """Deterministic release gate (T214)."""

    def __init__(self, min_coverage: float = 0.8) -> None:
        self._min_coverage = min_coverage

    def evaluate(self, rc: ReleaseCandidate) -> ReleaseVerdict:
        """Evaluate a release candidate (fail-closed, deterministic)."""
        if not rc.tests_passed:
            return ReleaseVerdict.NOGO
        if rc.coverage < self._min_coverage:
            return ReleaseVerdict.NOGO
        if not rc.certified:
            return ReleaseVerdict.NOGO
        return ReleaseVerdict.GO

    def release_hash(self, rc: ReleaseCandidate) -> str:
        v = self.evaluate(rc)
        return _hash(f"{rc.candidate_id}|{v.value}|{rc.coverage:.4f}")
