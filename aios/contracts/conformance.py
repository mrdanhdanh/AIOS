"""Conformance checks that lock frozen-contract behavior (TASK-064).

These checks are the *contract tests*: they must PASS before a task may be
marked DONE, and they fail-closed (any violation blocks). They are pure and
deterministic — the same registry always yields the same result.
"""

from __future__ import annotations

from typing import List

from .contract import ALL_SURFACES, Contract, ContractStatus, ContractSurface
from .registry import ContractRegistry

__all__ = [
    "check_contract_conformance",
    "check_registry_conformance",
    "ConformanceError",
]


class ConformanceError(Exception):
    """Raised when registry conformance is required but not satisfied."""


def check_contract_conformance(contract: Contract) -> List[str]:
    """Return a list of conformance violations for a single contract.

    An empty list means the contract conforms. Frozen contracts must carry an
    evidence reference and a backward-compatibility promise; every contract must
    declare one of the five known public surfaces.
    """
    violations: List[str] = []
    if contract.surface not in ALL_SURFACES:
        violations.append(
            f"{contract.name}: unknown surface {contract.surface!r}"
        )
    if contract.status is ContractStatus.FROZEN:
        if not contract.evidence_ref:
            violations.append(
                f"{contract.name}: FROZEN contract missing evidence_ref"
            )
        if not contract.compatibility:
            violations.append(
                f"{contract.name}: FROZEN contract missing compatibility promise"
            )
    return violations


def check_registry_conformance(registry: ContractRegistry) -> List[str]:
    """Return a list of conformance violations for the whole registry.

    Enforces:
      * every public surface (API/SCHEMA/EVENT/CAPABILITY/TOOL) has a FROZEN
        contract (no shadow / unregistered surface);
      * each FROZEN contract carries evidence + compatibility.
    Empty list == PASS (fail-closed otherwise).
    """
    violations: List[str] = []
    for contract in registry.list_contracts():
        violations.extend(check_contract_conformance(contract))
    for surface in ALL_SURFACES:
        if not registry.has_surface(surface):
            violations.append(
                f"public surface {surface.value} has no FROZEN contract registered"
            )
    return violations


def require_conformance(registry: ContractRegistry) -> None:
    """Raise :class:`ConformanceError` if the registry does not conform."""
    violations = check_registry_conformance(registry)
    if violations:
        raise ConformanceError(
            "contract conformance failed:\n  - " + "\n  - ".join(violations)
        )
