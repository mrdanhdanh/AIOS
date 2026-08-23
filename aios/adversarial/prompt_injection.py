"""TASK-170 — Prompt Injection Tester + Untrusted Artifact Isolation (M23).

Two capabilities: (1) probe whether prompt injection is sanitized; (2) verify
untrusted artifacts are isolated. Deterministic, fail-closed: an unsanitized
injection or a non-isolated untrusted artifact is a BREACH. UNKNOWN never
promoted to PASS (T078).
"""

from __future__ import annotations

from dataclasses import dataclass

from aios.adversarial._common import AdversarialError, _hash
from aios.adversarial.adversarial_evaluation import BLOCKED, BREACH, UNKNOWN


@dataclass(frozen=True)
class PromptInjectionAttack:
    attack_id: str
    injection_present: bool
    sanitized: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class PromptInjectionResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


@dataclass(frozen=True)
class ArtifactIsolationAttack:
    attack_id: str
    untrusted: bool
    isolated: bool

    def __post_init__(self) -> None:
        if not self.attack_id:
            raise AdversarialError("attack_id must be non-empty")


@dataclass(frozen=True)
class ArtifactIsolationResult:
    result_id: str
    attack_ref: str
    breached: bool
    status: str  # BLOCKED | BREACH | UNKNOWN


class PromptInjectionTester:
    """Probe whether prompt injection is sanitized."""

    def attack(self, a: PromptInjectionAttack) -> PromptInjectionResult:
        if not isinstance(a, PromptInjectionAttack):
            raise AdversarialError("attack must be a PromptInjectionAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = injection present AND not sanitized.
        breached = a.injection_present and not a.sanitized
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return PromptInjectionResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )


class UntrustedArtifactIsolation:
    """Verify untrusted artifacts are isolated."""

    def attack(self, a: ArtifactIsolationAttack) -> ArtifactIsolationResult:
        if not isinstance(a, ArtifactIsolationAttack):
            raise AdversarialError("attack must be an ArtifactIsolationAttack")
        if not a.attack_id:
            raise AdversarialError("attack_id must be non-empty (provenance)")

        # Breach = untrusted AND not isolated.
        breached = a.untrusted and not a.isolated
        status = BREACH if breached else BLOCKED
        result_id = _hash(f"{a.attack_id}|{breached}")
        return ArtifactIsolationResult(
            result_id=result_id,
            attack_ref=a.attack_id,
            breached=breached,
            status=status,
        )
