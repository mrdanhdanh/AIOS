"""TASK-156 — Test Adequacy Analyzer + Mutation Verifier (M22).

Deterministic mutation scoring: mutation_score = killed / total mutants.
Fail-closed: a suite with no provenance (empty id) is rejected; UNKNOWN is
never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class MutationSuite:
    suite_id: str
    mutants: int
    killed: int

    def __post_init__(self) -> None:
        if not self.suite_id:
            raise VerificationError("suite_id must be non-empty")
        if self.mutants < 0 or self.killed < 0:
            raise VerificationError("mutants/killed must be non-negative")
        if self.killed > self.mutants:
            raise VerificationError("killed cannot exceed mutants")


@dataclass(frozen=True)
class AdequacyReport:
    report_id: str
    suite_ref: str
    mutation_score: float
    status: str  # PASS | INSUFFICIENT | UNKNOWN


MUTATION_THRESHOLD = 0.5


class TestAdequacyAnalyzer:
    """Analyze test adequacy via mutation score."""

    def analyze(self, suite: MutationSuite) -> AdequacyReport:
        if not isinstance(suite, MutationSuite):
            raise VerificationError("suite must be a MutationSuite")
        if not suite.suite_id:
            raise VerificationError("suite_id must be non-empty (provenance)")

        if suite.mutants == 0:
            status = "UNKNOWN"
            score = 0.0
        else:
            score = suite.killed / suite.mutants
            status = "PASS" if score >= MUTATION_THRESHOLD else "INSUFFICIENT"

        report_id = _hash(f"{suite.suite_id}|{score:.4f}")
        return AdequacyReport(
            report_id=report_id,
            suite_ref=suite.suite_id,
            mutation_score=score,
            status=status,
        )
