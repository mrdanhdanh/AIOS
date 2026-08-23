"""TASK-176 — Risk Model + Classification (M24).

Classifies risk from likelihood x impact into LOW/MEDIUM/HIGH/CRITICAL levels.
Deterministic and fail-closed on invalid enum inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
LIKELIHOOD_LEVELS = ("RARE", "UNLIKELY", "POSSIBLE", "LIKELY", "CERTAIN")
IMPACT_LEVELS = ("NEGLIGIBLE", "MINOR", "MODERATE", "MAJOR", "SEVERE")

_LIKELIHOOD_SCORE = {"RARE": 1, "UNLIKELY": 2, "POSSIBLE": 3, "LIKELY": 4, "CERTAIN": 5}
_IMPACT_SCORE = {"NEGLIGIBLE": 1, "MINOR": 2, "MODERATE": 3, "MAJOR": 4, "SEVERE": 5}


@dataclass(frozen=True)
class RiskAsset:
    asset_id: str
    likelihood: str
    impact: str

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise QualityGateError("asset_id must be non-empty")
        if self.likelihood not in LIKELIHOOD_LEVELS:
            raise QualityGateError(f"invalid likelihood: {self.likelihood}")
        if self.impact not in IMPACT_LEVELS:
            raise QualityGateError(f"invalid impact: {self.impact}")


@dataclass(frozen=True)
class RiskReport:
    report_id: str
    asset_ref: str
    score: int
    level: str


class RiskModel:
    """Classify risk from likelihood x impact."""

    def classify(self, asset: RiskAsset) -> RiskReport:
        if not isinstance(asset, RiskAsset):
            raise QualityGateError("asset must be a RiskAsset")
        score = _LIKELIHOOD_SCORE[asset.likelihood] * _IMPACT_SCORE[asset.impact]
        if score <= 4:
            level = "LOW"
        elif score <= 9:
            level = "MEDIUM"
        elif score <= 16:
            level = "HIGH"
        else:
            level = "CRITICAL"
        report_id = _hash(f"{asset.asset_id}|{score}|{level}")
        return RiskReport(report_id=report_id, asset_ref=asset.asset_id, score=score, level=level)
