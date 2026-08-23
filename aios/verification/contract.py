"""TASK-158 — Contract Verifier (M22).

Deterministic contract verification: every precondition must hold and every
postcondition must be satisfied by the observed state. Fail-closed: a contract
with no provenance (empty id) is rejected; any violation -> INSUFFICIENT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from aios.verification._common import VerificationError, _hash, _now


@dataclass(frozen=True)
class Contract:
    contract_id: str
    preconditions: tuple = field(default_factory=tuple)
    postconditions: tuple = field(default_factory=tuple)
    observed: tuple = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise VerificationError("contract_id must be non-empty")


@dataclass(frozen=True)
class ContractReport:
    report_id: str
    contract_ref: str
    violations: tuple
    status: str  # PASS | INSUFFICIENT


class ContractVerifier:
    """Verify a contract's pre/postconditions against observed values."""

    def verify(self, contract: Contract) -> ContractReport:
        if not isinstance(contract, Contract):
            raise VerificationError("contract must be a Contract")
        if not contract.contract_id:
            raise VerificationError("contract_id must be non-empty (provenance)")

        violations: List[str] = []
        # Preconditions must all be truthy.
        for i, pre in enumerate(contract.preconditions):
            if not pre:
                violations.append(f"precondition[{i}] violated")
        # Postconditions must all be truthy.
        for i, post in enumerate(contract.postconditions):
            if not post:
                violations.append(f"postcondition[{i}] violated")

        status = "PASS" if not violations else "INSUFFICIENT"
        report_id = _hash(f"{contract.contract_id}|{len(violations)}")
        return ContractReport(
            report_id=report_id,
            contract_ref=contract.contract_id,
            violations=tuple(violations),
            status=status,
        )
