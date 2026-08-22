"""AIOS public contract freeze (TASK-064).

Versioned, externally-visible contracts for the five public surfaces
(API / SCHEMA / EVENT / CAPABILITY / TOOL). Frozen contracts are immutable
except through a version bump + ADR (fail-closed, no silent change).

Public API:
    Contract, ContractStatus, ContractSurface, ALL_SURFACES
    ContractRegistry, ContractFreezeError, ContractNotRegisteredError,
    build_default_registry
    check_contract_conformance, check_registry_conformance, require_conformance,
    ConformanceError
"""

from __future__ import annotations

from .contract import (
    ALL_SURFACES,
    Contract,
    ContractStatus,
    ContractSurface,
)
from .conformance import (
    ConformanceError,
    check_contract_conformance,
    check_registry_conformance,
    require_conformance,
)
from .registry import (
    ContractFreezeError,
    ContractNotRegisteredError,
    ContractRegistry,
    build_default_registry,
)

__all__ = [
    "Contract",
    "ContractStatus",
    "ContractSurface",
    "ALL_SURFACES",
    "ContractRegistry",
    "ContractFreezeError",
    "ContractNotRegisteredError",
    "build_default_registry",
    "check_contract_conformance",
    "check_registry_conformance",
    "require_conformance",
    "ConformanceError",
]
