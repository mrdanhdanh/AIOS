"""TASK-162 — Replay & Flaky Detector (M22).

Deterministic flakiness detection: a replay is flaky when repeated runs do not
produce identical outcomes. Fail-closed: a run with no provenance (empty id)
is rejected; flaky -> INSUFFICIENT (never promoted).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class ReplayRun:
    run_id: str
    outcomes: tuple = field(default_factory=tuple)  # repeated run outcomes

    def __post_init__(self) -> None:
        if not self.run_id:
            raise VerificationError("run_id must be non-empty")


@dataclass(frozen=True)
class FlakyReport:
    report_id: str
    run_ref: str
    flaky: bool
    status: str  # PASS | INSUFFICIENT


class ReplayFlakyDetector:
    """Detect flakiness across repeated replay outcomes."""

    def detect(self, run: ReplayRun) -> FlakyReport:
        if not isinstance(run, ReplayRun):
            raise VerificationError("run must be a ReplayRun")
        if not run.run_id:
            raise VerificationError("run_id must be non-empty (provenance)")
        if len(run.outcomes) == 0:
            raise VerificationError("outcomes must be provided")

        flaky = len(set(run.outcomes)) > 1
        status = "INSUFFICIENT" if flaky else "PASS"
        report_id = _hash(f"{run.run_id}|{flaky}")
        return FlakyReport(
            report_id=report_id,
            run_ref=run.run_id,
            flaky=flaky,
            status=status,
        )
