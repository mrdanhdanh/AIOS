"""TASK-159 — Regression Verifier (M22).

Deterministic regression detection: a metric regresses when current is worse
than baseline (direction-aware). Fail-closed: a check with no provenance
(empty id) is rejected; regression -> INSUFFICIENT (never promoted).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class RegressionCheck:
    check_id: str
    metric: str
    baseline: float
    current: float
    higher_is_better: bool = True

    def __post_init__(self) -> None:
        if not self.check_id:
            raise VerificationError("check_id must be non-empty")
        if not self.metric:
            raise VerificationError("metric must be non-empty")


@dataclass(frozen=True)
class RegressionReport:
    report_id: str
    check_ref: str
    regressed: bool
    status: str  # PASS | INSUFFICIENT


class RegressionVerifier:
    """Detect whether a metric regressed relative to its baseline."""

    def verify(self, check: RegressionCheck) -> RegressionReport:
        if not isinstance(check, RegressionCheck):
            raise VerificationError("check must be a RegressionCheck")
        if not check.check_id:
            raise VerificationError("check_id must be non-empty (provenance)")

        if check.higher_is_better:
            regressed = check.current < check.baseline
        else:
            regressed = check.current > check.baseline

        status = "INSUFFICIENT" if regressed else "PASS"
        report_id = _hash(f"{check.check_id}|{regressed}")
        return RegressionReport(
            report_id=report_id,
            check_ref=check.check_id,
            regressed=regressed,
            status=status,
        )
