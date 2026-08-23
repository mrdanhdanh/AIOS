"""TASK-185 — Coding Evaluation Contract (M25).

A standard contract for coding evaluation: declares dimensions and thresholds.
Fail-closed: a contract with no dimensions or invalid threshold is INSUFFICIENT;
UNKNOWN is never promoted to PASS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from aios.evaluation._common import EvaluationError, _hash

VALID_STATUSES = ("PASS", "INSUFFICIENT", "UNKNOWN")


@dataclass(frozen=True)
class EvaluationContract:
    contract_id: str
    name: str
    dimensions: Tuple[str, ...]
    thresholds: Tuple[float, ...]  # parallel to dimensions

    def __post_init__(self) -> None:
        if not self.contract_id:
            raise EvaluationError("contract_id must be non-empty")
        if not self.name:
            raise EvaluationError("name must be non-empty")
        if len(self.dimensions) != len(self.thresholds):
            raise EvaluationError("dimensions and thresholds length mismatch")
        for t in self.thresholds:
            if not (0.0 <= t <= 1.0):
                raise EvaluationError(f"threshold out of range: {t}")


@dataclass(frozen=True)
class ContractValidationReport:
    report_id: str
    contract_ref: str
    status: str
    dimension_count: int


class EvaluationContractValidator:
    """Validate a coding evaluation contract deterministically."""

    def validate(self, contract: EvaluationContract) -> ContractValidationReport:
        if not isinstance(contract, EvaluationContract):
            raise EvaluationError("contract must be an EvaluationContract")
        if not contract.dimensions:
            status = "UNKNOWN"
        else:
            status = "PASS"
        report_id = _hash(f"{contract.contract_id}|{status}|{len(contract.dimensions)}")
        return ContractValidationReport(
            report_id=report_id,
            contract_ref=contract.contract_id,
            status=status,
            dimension_count=len(contract.dimensions),
        )
