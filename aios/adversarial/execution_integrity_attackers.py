"""TASK-171 — Execution Integrity Attackers (M23).

Probe whether execution integrity holds under tamper. Deterministic,
fail-closed: a tamper attempt that passes integrity verification is a BREACH;
detected tamper or no tamper is BLOCKED. UNKNOWN never promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class ExecutionIntegrityAttack:
    attack_id: str
    tamper_attempt: bool
    integrity_verified: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class ExecutionIntegrityResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class ExecutionIntegrityAttacker:
    """Probe execution integrity under tamper attempts."""

    def attack(self, a: ExecutionIntegrityAttack) -> ExecutionIntegrityResult:
        if not isinstance(a, ExecutionIntegrityAttack):
            raise AdversarialError("attack must be an ExecutionIntegrityAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = tamper attempt AND integrity still verifies (undetected).
        breached = a.tamper_attempt and a.integrity_verified
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return ExecutionIntegrityResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
