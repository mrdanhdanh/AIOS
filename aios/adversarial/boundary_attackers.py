"""TASK-173 — Boundary Attackers (M23).

Probe whether boundary escapes are prevented. Deterministic, fail-closed: an
escape attempt that is not contained is a BREACH; a contained attempt or no
attempt is BLOCKED. UNKNOWN never promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class BoundaryAttack:
    attack_id: str
    escape_attempt: bool
    contained: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class BoundaryResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class BoundaryAttacker:
    """Probe boundary-escape prevention."""

    def attack(self, a: BoundaryAttack) -> BoundaryResult:
        if not isinstance(a, BoundaryAttack):
            raise AdversarialError("attack must be a BoundaryAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = escape attempt AND not contained.
        breached = a.escape_attempt and not a.contained
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return BoundaryResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
