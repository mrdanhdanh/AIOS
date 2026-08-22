"""Contract registry enforcing the T064 public-contract freeze policy.

The registry is the single source of truth for which public surfaces are
frozen and at what version. It is fail-closed: any attempt to silently change a
``FROZEN`` contract (same version, or a change without an ADR reference) raises
:class:`ContractFreezeError`. A breaking change (major version bump) is only
permitted when accompanied by an ``adr_ref`` and opens a deprecation window.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Optional

from .contract import (
    ALL_SURFACES,
    Contract,
    ContractStatus,
    ContractSurface,
    DEFAULT_DEPRECATION_WINDOW,
)

__all__ = [
    "ContractFreezeError",
    "ContractNotRegisteredError",
    "ContractRegistry",
    "build_default_registry",
]


class ContractFreezeError(Exception):
    """Raised when a change to a FROZEN contract violates the freeze policy.

    Fail-closed: a frozen contract must never change silently. Any mutation
    requires a version bump and an ADR reference; a breaking change additionally
    requires a major version bump.
    """


class ContractNotRegisteredError(Exception):
    """Raised when a public surface has no registered contract.

    Enforces the "no shadow contract" rule: every public surface must be
    registered before it can be looked up / relied upon.
    """


class ContractRegistry:
    """Registry of public contracts with freeze-safety enforcement."""

    def __init__(self) -> None:
        self._contracts: Dict[str, Contract] = {}
        # ADR reference recorded at last freeze / change time, per contract name.
        self._adr: Dict[str, str] = {}
        # Deprecation window opened by the most recent breaking (major) change.
        self._deprecation: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register(self, contract: Contract, *, adr_ref: Optional[str] = None) -> Contract:
        """Register or update a contract.

        Updating an already-``FROZEN`` contract is governed by
        :meth:`_require_valid_change` (version bump + ADR required, no silent
        change). Returns the stored contract.
        """
        if contract.name in self._contracts:
            self._require_valid_change(self._contracts[contract.name], contract, adr_ref)
        self._contracts[contract.name] = contract
        if adr_ref:
            self._adr[contract.name] = adr_ref
        return contract

    def _require_valid_change(
        self, existing: Contract, new: Contract, adr_ref: Optional[str]
    ) -> None:
        """Enforce freeze policy for an update to an existing contract."""
        if existing.status is not ContractStatus.FROZEN:
            # DRAFT / DEPRECATED contracts may change freely.
            return
        # 1) No silent change: the version MUST change.
        if new.version == existing.version:
            raise ContractFreezeError(
                f"silent change to FROZEN contract {existing.name!r} is forbidden; "
                f"bump the version (currently {existing.version})"
            )
        # 2) Any change to a frozen contract must be documented by an ADR.
        if not adr_ref:
            raise ContractFreezeError(
                f"change to FROZEN contract {existing.name!r} requires an adr_ref"
            )
        # 3) A breaking change (major bump) opens a deprecation window.
        if new.major > existing.major:
            self._deprecation[existing.name] = DEFAULT_DEPRECATION_WINDOW

    # ------------------------------------------------------------------ #
    # Lookup
    # ------------------------------------------------------------------ #
    def lookup(self, name: str) -> Contract:
        """Return a registered contract by name.

        Raises :class:`ContractNotRegisteredError` if no contract exists, so an
        unregistered public surface is blocked (no shadow contract).
        """
        if name not in self._contracts:
            raise ContractNotRegisteredError(
                f"public surface {name!r} has no registered contract (no shadow contract)"
            )
        return self._contracts[name]

    def adr_ref(self, name: str) -> Optional[str]:
        """Return the ADR reference recorded for a contract (or ``None``)."""
        return self._adr.get(name)

    def deprecation_window(self, name: str) -> Optional[str]:
        """Return the deprecation window opened by the last breaking change."""
        return self._deprecation.get(name)

    # ------------------------------------------------------------------ #
    # Lifecycle transitions
    # ------------------------------------------------------------------ #
    def freeze(self, name: str, *, adr_ref: str, evidence_ref: Optional[str] = None) -> Contract:
        """Freeze a contract. Requires an ``adr_ref`` (documentation)."""
        if not adr_ref:
            raise ContractFreezeError(f"freeze of {name!r} requires an adr_ref")
        contract = self.lookup(name)
        frozen = replace(
            contract,
            status=ContractStatus.FROZEN,
            evidence_ref=evidence_ref or contract.evidence_ref,
        )
        self._contracts[name] = frozen
        self._adr[name] = adr_ref
        return frozen

    def deprecate(self, name: str, *, adr_ref: Optional[str] = None) -> Contract:
        """Mark a contract DEPRECATED (soft retirement)."""
        contract = self.lookup(name)
        deprecated = replace(contract, status=ContractStatus.DEPRECATED)
        self._contracts[name] = deprecated
        if adr_ref:
            self._adr[name] = adr_ref
        return deprecated

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #
    def list_contracts(self) -> List[Contract]:
        """Return all registered contracts (deterministic order by name)."""
        return [self._contracts[n] for n in sorted(self._contracts)]

    def frozen_contracts(self) -> List[Contract]:
        """Return all FROZEN contracts."""
        return [c for c in self.list_contracts() if c.is_frozen]

    def has_surface(self, surface: ContractSurface) -> bool:
        """True if at least one FROZEN contract covers ``surface``."""
        return any(c.surface == surface and c.is_frozen for c in self._contracts.values())

    def covered_surfaces(self) -> List[ContractSurface]:
        """Return the public surfaces that have a FROZEN contract."""
        return [s for s in ALL_SURFACES if self.has_surface(s)]


def build_default_registry() -> ContractRegistry:
    """Populate a registry with the five frozen 1.0 public surfaces.

    API / SCHEMA / EVENT / CAPABILITY / TOOL are each registered as a FROZEN
    contract at version ``1.0.0`` with a backward-compatibility promise and an
    evidence reference (the T064 ADR).
    """
    registry = ContractRegistry()
    surfaces = [
        (ContractSurface.API, "aios.api.public", "2.0.0"),
        (ContractSurface.SCHEMA, "aios.schema.public", "2.0.0"),
        (ContractSurface.EVENT, "aios.event.public", "2.0.0"),
        (ContractSurface.CAPABILITY, "aios.capability.public", "2.0.0"),
        (ContractSurface.TOOL, "aios.tool.public", "2.0.0"),
    ]
    for surface, name, compat in surfaces:
        contract = Contract(
            name=name,
            version="1.0.0",
            status=ContractStatus.FROZEN,
            surface=surface,
            compatibility=compat,
            evidence_ref="adr:T064-public-contract-freeze",
        )
        registry.register(contract, adr_ref="adr:T064-public-contract-freeze")
    return registry
