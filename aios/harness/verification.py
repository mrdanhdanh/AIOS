"""Verification pipeline — checks preconditions, postconditions, invariants.

AC-030-01: Execution succeeds but post-condition fails → FAIL.
AC-030-03: Postconditions checked deterministically.
AC-030-05: Every run creates traceable Evidence Package.
AC-030-08: Verdict not based solely on exit_code==0.
AC-030-09: Missing/insufficient evidence → INCONCLUSIVE.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class EvidencePackage:
    """Traceable evidence for a verification run."""
    evidence_id: str
    run_id: str
    producer: str = "verification_pipeline"
    checks_passed: int = 0
    checks_failed: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id, "run_id": self.run_id,
            "checks_passed": self.checks_passed, "checks_failed": self.checks_failed,
        }


@dataclass
class VerificationResult:
    """Result of verification pipeline."""
    verdict: Verdict = Verdict.INCONCLUSIVE
    preconditions_met: bool = True
    postconditions_met: bool = True
    invariants_met: bool = True
    evidence: EvidencePackage | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "preconditions_met": self.preconditions_met,
            "postconditions_met": self.postconditions_met,
            "invariants_met": self.invariants_met,
            "evidence": self.evidence.to_dict() if self.evidence else None,
        }


class VerificationPipeline:
    """Runs preconditions → postconditions → invariants → evidence → verdict."""

    def __init__(self) -> None:
        self._preconditions: list[Callable[[], bool]] = []
        self._postconditions: list[Callable[[], bool]] = []
        self._invariants: list[Callable[[], bool]] = []

    def add_precondition(self, check: Callable[[], bool]) -> None:
        self._preconditions.append(check)

    def add_postcondition(self, check: Callable[[], bool]) -> None:
        self._postconditions.append(check)

    def add_invariant(self, check: Callable[[], bool]) -> None:
        self._invariants.append(check)

    def verify(self, run_id: str = "") -> VerificationResult:
        """Run all checks and produce verdict."""
        pre_met = all(fn() for fn in self._preconditions) if self._preconditions else True
        post_met = all(fn() for fn in self._postconditions) if self._postconditions else True
        inv_met = all(fn() for fn in self._invariants) if self._invariants else True

        checks_passed = sum(1 for fn in self._preconditions if fn())
        checks_passed += sum(1 for fn in self._postconditions if fn())
        checks_passed += sum(1 for fn in self._invariants if fn())
        total_checks = len(self._preconditions) + len(self._postconditions) + len(self._invariants)
        checks_failed = total_checks - checks_passed

        evidence = EvidencePackage(
            evidence_id=f"ev-{hashlib.sha256(run_id.encode()).hexdigest()[:8]}",
            run_id=run_id,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
        )

        # AC-030-01: postcondition fail → FAIL
        if not pre_met:
            verdict = Verdict.FAIL
        elif not post_met:
            verdict = Verdict.FAIL
        elif not inv_met:
            verdict = Verdict.FAIL
        elif total_checks == 0:
            verdict = Verdict.INCONCLUSIVE  # AC-030-09
        else:
            verdict = Verdict.PASS

        return VerificationResult(
            verdict=verdict,
            preconditions_met=pre_met,
            postconditions_met=post_met,
            invariants_met=inv_met,
            evidence=evidence,
        )
