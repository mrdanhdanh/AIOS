"""TASK-169 — Certificate Attackers (M23).

Probe whether a certificate can be forged and accepted. Deterministic,
fail-closed: a forged certificate that still verifies is a BREACH; a forged cert
that fails verification, or no forgery, is BLOCKED. UNKNOWN never promoted (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class CertificateAttack:
    attack_id: str
    forged: bool
    verified: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class CertificateResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class CertificateAttacker:
    """Probe certificate forgery acceptance."""

    def attack(self, a: CertificateAttack) -> CertificateResult:
        if not isinstance(a, CertificateAttack):
            raise AdversarialError("attack must be a CertificateAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = forged AND still verified (forgery undetected).
        breached = a.forged and a.verified
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return CertificateResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
