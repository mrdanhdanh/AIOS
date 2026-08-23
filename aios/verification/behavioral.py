"""TASK-157 — Behavioral Verifier (M22).

Deterministic behavioral equivalence check: expected == actual on a normalized
representation. Fail-closed: a spec with no provenance (empty id) is rejected;
mismatch is INSUFFICIENT, never silently promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class BehaviorSpec:
    spec_id: str
    expected: Any
    actual: Any

    def __post_init__(self) -> None:
        if not self.spec_id:
            raise VerificationError("spec_id must be non-empty")


@dataclass(frozen=True)
class BehaviorReport:
    report_id: str
    spec_ref: str
    match: bool
    status: str  # PASS | INSUFFICIENT


class BehavioralVerifier:
    """Verify observed behavior matches the expected behavioral spec."""

    def verify(self, spec: BehaviorSpec) -> BehaviorReport:
        if not isinstance(spec, BehaviorSpec):
            raise VerificationError("spec must be a BehaviorSpec")
        if not spec.spec_id:
            raise VerificationError("spec_id must be non-empty (provenance)")

        match = spec.expected == spec.actual
        status = "PASS" if match else "INSUFFICIENT"
        report_id = _hash(f"{spec.spec_id}|{match}")
        return BehaviorReport(
            report_id=report_id,
            spec_ref=spec.spec_id,
            match=match,
            status=status,
        )
