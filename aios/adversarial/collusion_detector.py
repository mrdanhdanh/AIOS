"""TASK-174 — Collusion Detector + Resilience Score + Attack Corpus Regression (M23).

Integration capability aggregating attacker results: detect collusion (multiple
breaches), compute a resilience score, and verify the attack corpus has not
regressed. Deterministic, fail-closed: any result with no provenance (empty id)
is rejected; a breach is never promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN

COLLUSION_THRESHOLD = 2  # >= this many breaches indicates collusion
RESILIENCE_THRESHOLD = 0.8


@dataclass(frozen=True)
class CollusionReport:
    report_id: str
    attack_refs: tuple
    collusion_detected: bool
    status: str  # PASS | INSUFFICIENT | UNKNOWN


@dataclass(frozen=True)
class ResilienceReport:
    report_id: str
    score: float
    status: str  # PASS | INSUFFICIENT | UNKNOWN


@dataclass(frozen=True)
class AttackCorpusRegression:
    report_id: str
    regressed: bool
    status: str  # PASS | INSUFFICIENT


class CollusionDetector:
    """Detect collusion, score resilience, and check corpus regression."""

    def detect(self, results: List) -> CollusionReport:
        if not results:
            raise AdversarialError("results must be provided")
        for r in results:
            if not hasattr(r, "attack_id") or not r.attack_id:
                raise AdversarialError("attack_id must be non-empty (provenance)")

        breaches = sum(1 for r in results if getattr(r, "status", None) == BREACH)
        collusion = breaches >= COLLUSION_THRESHOLD
        status = "INSUFFICIENT" if collusion else "PASS"
        report_id = _hash("|".join(f"{r.attack_id}:{getattr(r,'status',None)}" for r in results))
        return CollusionReport(
            report_id=report_id,
            attack_refs=tuple(r.attack_id for r in results),
            collusion_detected=collusion,
            status=status,
        )

    def score_resilience(self, results: List) -> ResilienceReport:
        if not results:
            raise AdversarialError("results must be provided")
        total = len(results)
        blocked = sum(1 for r in results if getattr(r, "status", None) == BLOCKED)
        score = blocked / total
        status = "PASS" if score >= RESILIENCE_THRESHOLD else "INSUFFICIENT"
        report_id = _hash(f"{score:.4f}|{total}")
        return ResilienceReport(report_id=report_id, score=score, status=status)

    def check_corpus_regression(self, baseline: int, current: int) -> AttackCorpusRegression:
        if baseline < 0 or current < 0:
            raise AdversarialError("baseline/current must be non-negative")
        regressed = current < baseline
        status = "INSUFFICIENT" if regressed else "PASS"
        report_id = _hash(f"{baseline}|{current}|{regressed}")
        return AttackCorpusRegression(report_id=report_id, regressed=regressed, status=status)
