"""TASK-166 — Evidence Attackers (M23).

Probe whether evidence can be tampered undetected. Deterministic, fail-closed:
a tampered-but-undetected evidence is a BREACH; detected tamper or no tamper is
BLOCKED. UNKNOWN never promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class EvidenceAttack:
    attack_id: str
    tampered: bool
    detected: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class EvidenceAttackResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class EvidenceAttacker:
    """Attempt to tamper with evidence and check detection."""

    def attack(self, a: EvidenceAttack) -> EvidenceAttackResult:
        if not isinstance(a, EvidenceAttack):
            raise AdversarialError("attack must be an EvidenceAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = tampered AND not detected (integrity check missed it).
        breached = a.tampered and not a.detected
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return EvidenceAttackResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
