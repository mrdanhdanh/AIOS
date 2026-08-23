"""TASK-200 — Risk Engine (M26).

Risk assessment for coding changes, converging Risk Model (T176) and Trust
(T164). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from aios.coding_edition._common import CodingEditionError, _hash


class RiskLevel(str, Enum):
    """Risk severity bands (T200)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RiskModel:
    """A single weighted risk factor (T200)."""

    factor: str
    weight: float
    description: str = ""

    def __post_init__(self) -> None:
        if not self.factor:
            raise CodingEditionError("factor is required (T001 Rule 1, immutable).")
        if self.weight < 0.0 or self.weight > 1.0:
            raise CodingEditionError("weight must be in [0,1].")


@dataclass
class RiskInput:
    """Observed signals for a change under assessment (T200)."""

    change_id: str
    signals: Dict[str, float] = field(default_factory=dict)  # factor -> severity 0..1

    def __post_init__(self) -> None:
        if not self.change_id:
            raise CodingEditionError("change_id is required (T001 Rule 1, immutable).")
        for k, v in self.signals.items():
            if v < 0.0 or v > 1.0:
                raise CodingEditionError(f"signal '{k}' severity must be in [0,1].")


class RiskEngine:
    """Deterministic risk engine (T200)."""

    def __init__(self, models: Optional[List[RiskModel]] = None) -> None:
        self._models: List[RiskModel] = list(models or [])

    def add(self, model: RiskModel) -> None:
        self._models.append(model)

    def assess(self, inp: RiskInput) -> Tuple[float, RiskLevel]:
        """Compute weighted risk score in [0,1] and band (fail-closed)."""
        if not self._models:
            return 0.0, RiskLevel.UNKNOWN
        total_w = sum(m.weight for m in self._models)
        if total_w <= 0.0:
            return 0.0, RiskLevel.UNKNOWN
        score = 0.0
        for m in self._models:
            sev = inp.signals.get(m.factor, 0.0)
            score += m.weight * sev
        score = min(1.0, score / total_w)
        return score, self._band(score)

    @staticmethod
    def _band(score: float) -> RiskLevel:
        if score < 0.25:
            return RiskLevel.LOW
        if score < 0.5:
            return RiskLevel.MEDIUM
        if score < 0.75:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def risk_hash(self, inp: RiskInput) -> str:
        score, level = self.assess(inp)
        return _hash(f"{inp.change_id}|{score:.4f}|{level.value}")
