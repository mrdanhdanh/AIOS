"""TASK-165 — Adversarial Evaluation Harness (M23).

Aggregates attack results into an adversarial resilience report. Deterministic,
fail-closed: any attack with no provenance (empty id) is rejected; a BREACH is
never promoted to PASS (T078). UNKNOWN is never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from aios.adversarial._common import AdversarialError, _hash

# Attack result statuses emitted by individual attackers.
BLOCKED = "BLOCKED"   # attack failed to breach the system (good)
BREACH = "BREACH"     # attack succeeded (bad)
UNKNOWN = "UNKNOWN"   # inconclusive, never promoted to PASS


@dataclass(frozen=True)
class AttackResult:
    attack_id: str
    attack_type: str
    status: str  # BLOCKED | BREACH | UNKNOWN

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")
        if self.status not in (BLOCKED, BREACH, UNKNOWN):
            raise AdversarialError(f"invalid attack status: {self.status}")


@dataclass(frozen=True)
class AdversarialReport:
    report_id: str
    attack_refs: tuple
    breached: bool
    status: str  # PASS | INSUFFICIENT | UNKNOWN


class AdversarialEvaluationHarness:
    """Aggregate attack results into a resilience verdict."""

    def evaluate(self, results: List[AttackResult]) -> AdversarialReport:
        if not results:
            raise AdversarialError("results must be provided")
        for r in results:
            if not isinstance(r, AttackResult):
                raise AdversarialError("each result must be an AttackResult")
            if not r.attack_id:
                raise AdversarialError("attack_id must be non-empty (provenance)")

        breached = any(r.status == BREACH for r in results)
        unknown = any(r.status == UNKNOWN for r in results)

        if breached:
            status = "INSUFFICIENT"
        elif unknown:
            status = UNKNOWN
        else:
            status = "PASS"

        report_id = _hash("|".join(f"{r.attack_id}:{r.status}" for r in results))
        return AdversarialReport(
            report_id=report_id,
            attack_refs=tuple(r.attack_id for r in results),
            breached=breached,
            status=status,
        )
