"""TASK-167 — Test Weakness Attackers (M23).

Probe whether tests are weak (a mutation survives). Deterministic, fail-closed:
a surviving mutation (not killed) is a BREACH (weak test); a killed mutation is
BLOCKED. UNKNOWN never promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class TestWeaknessAttack:
    attack_id: str
    mutation_killed: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class TestWeaknessResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class TestWeaknessAttacker:
    """Probe test weakness via mutation survival."""

    def attack(self, a: TestWeaknessAttack) -> TestWeaknessResult:
        if not isinstance(a, TestWeaknessAttack):
            raise AdversarialError("attack must be a TestWeaknessAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = mutation survived (test did not catch it).
        breached = not a.mutation_killed
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return TestWeaknessResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
