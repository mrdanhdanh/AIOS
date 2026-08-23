"""TASK-172 — Environment / Dependency Attackers (M23).

Probe whether malicious dependencies are contained. Deterministic, fail-closed:
a malicious dependency that is not blocked is a BREACH; a blocked malicious dep
or a clean dep is BLOCKED. UNKNOWN never promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class EnvironmentDependencyAttack:
    attack_id: str
    malicious_dep: bool
    blocked: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class EnvironmentDependencyResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class EnvironmentDependencyAttacker:
    """Probe malicious dependency containment."""

    def attack(self, a: EnvironmentDependencyAttack) -> EnvironmentDependencyResult:
        if not isinstance(a, EnvironmentDependencyAttack):
            raise AdversarialError("attack must be an EnvironmentDependencyAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = malicious dependency AND not blocked.
        breached = a.malicious_dep and not a.blocked
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return EnvironmentDependencyResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
