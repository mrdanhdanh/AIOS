"""Meta-Harness / Verify-the-Verifier — harness-of-harness (TASK-091, M13).

Canonical meta contract:

    MetaCheck
    ├── harness_under_test
    ├── known_answer: expected verdict
    ├── known_answer_correct: bool
    ├── mutation_detected: bool
    ├── verifier_locked: bool
    └── evidence_ref

Safety properties (all fail-closed / verifier-lock / provenance / deterministic):
* Fail-closed meta — harness giving a wrong verdict -> meta FAIL (no certify).
* Mutation detection — a mutated input MUST be detected (else meta FAIL).
* Verifier lock — the verifier is locked per run via T078 (IntegrityChecker).
* Evidence required — every meta-run carries provenance (T001 Rule 5).
* Deterministic — same meta-input + same harness -> same meta-result.
* No parallel meta system — uses Harness (T030/T032) + Integrity (T078).

Integration: imports ``aios.verification_integrity.integrity`` (IntegrityChecker,
VerifierLock) and ``aios.harness_coverage.coverage`` (CoverageReport, Readiness).
No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from aios.harness_coverage.coverage import CoverageReport, Readiness
from aios.verification_integrity.integrity import IntegrityChecker

# A harness-under-test takes a subject and returns a verdict string.
HarnessFn = Callable[[Any], str]


class MetaVerdict(str, Enum):
    """The meta-verifier's verdict on the harness-under-test."""

    PASS = "pass"
    FAIL = "fail"


@dataclass
class MetaCheck:
    """One meta-check against a harness-under-test."""

    harness_under_test: str
    known_answer: str  # expected verdict for the known-answer test
    known_answer_correct: bool
    mutation_detected: bool
    verifier_locked: bool
    kind: str = "known_answer"  # "known_answer" | "mutation"
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "harness_under_test": self.harness_under_test,
            "known_answer": self.known_answer,
            "known_answer_correct": self.known_answer_correct,
            "mutation_detected": self.mutation_detected,
            "verifier_locked": self.verifier_locked,
            "kind": self.kind,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class MetaResult:
    """Fail-closed aggregate of meta-checks."""

    checks: list[MetaCheck]
    verdict: MetaVerdict
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [c.to_dict() for c in self.checks],
            "verdict": self.verdict.value,
            "evidence_ref": self.evidence_ref,
        }


class MetaHarness:
    """Runs known-answer + mutation tests over a harness-under-test."""

    def __init__(self, integrity_checker: Optional[IntegrityChecker] = None) -> None:
        self._integrity = integrity_checker or IntegrityChecker()

    # -- known-answer ----------------------------------------------------------

    def known_answer_check(
        self,
        harness_name: str,
        harness_fn: HarnessFn,
        subject: Any,
        expected_verdict: str,
        run_id: str = "",
    ) -> MetaCheck:
        """The harness MUST return the known verdict for the sample input."""
        actual = str(harness_fn(subject))
        correct = actual == expected_verdict
        run_key = run_id or harness_name
        self._integrity.lock_verifier(run_key, harness_name)
        verifier_locked = not self._integrity.verifier_changed(run_key, harness_name)
        ev_id = f"mev-{hashlib.sha256((harness_name + expected_verdict).encode()).hexdigest()[:8]}"
        return MetaCheck(
            harness_under_test=harness_name,
            known_answer=expected_verdict,
            known_answer_correct=correct,
            mutation_detected=False,
            verifier_locked=verifier_locked,
            kind="known_answer",
            evidence_ref=ev_id,
        )

    # -- mutation --------------------------------------------------------------

    def mutation_check(
        self,
        harness_name: str,
        harness_fn: HarnessFn,
        original: Any,
        mutated: Any,
        run_id: str = "",
    ) -> MetaCheck:
        """A mutated input MUST produce a different verdict (detection)."""
        orig = str(harness_fn(original))
        mut = str(harness_fn(mutated))
        detected = orig != mut
        run_key = run_id or harness_name
        self._integrity.lock_verifier(run_key, harness_name)
        verifier_locked = not self._integrity.verifier_changed(run_key, harness_name)
        ev_id = f"mev-{hashlib.sha256((harness_name + 'mutation').encode()).hexdigest()[:8]}"
        return MetaCheck(
            harness_under_test=harness_name,
            known_answer="",
            known_answer_correct=True,
            mutation_detected=detected,
            verifier_locked=verifier_locked,
            kind="mutation",
            evidence_ref=ev_id,
        )

    # -- aggregate -------------------------------------------------------------

    def evaluate(self, checks: list[MetaCheck], evidence_ref: str = "") -> MetaResult:
        """Fail-closed: any wrong known-answer OR undetected mutation OR unlocked
        verifier -> meta FAIL. Each check is judged by its own kind."""
        ok = all(self._check_ok(c) for c in checks)
        return MetaResult(
            checks=checks,
            verdict=MetaVerdict.PASS if ok else MetaVerdict.FAIL,
            evidence_ref=evidence_ref,
        )

    @staticmethod
    def _check_ok(c: MetaCheck) -> bool:
        if c.kind == "mutation":
            return c.mutation_detected and c.verifier_locked
        # known_answer (default)
        return c.known_answer_correct and c.verifier_locked

    # -- coverage integration (T090) ------------------------------------------

    def require_readiness(self, coverage_report: CoverageReport) -> bool:
        """Meta only runs when the harness coverage is READY (T090)."""
        return coverage_report.readiness == Readiness.READY

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, result: MetaResult) -> bool:
        return bool(result.evidence_ref) and all(
            bool(c.evidence_ref) for c in result.checks
        )

    def result_hash(self, result: MetaResult) -> str:
        """Deterministic hash (same checks + verdict -> same hash)."""
        payload = {
            "verdict": result.verdict.value,
            "checks": sorted(c.to_dict() for c in result.checks),
            "evidence_ref": result.evidence_ref,
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
