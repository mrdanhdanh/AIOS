"""Public contract model for the AIOS 1.0 freeze (TASK-064).

A *contract* is a named, versioned, externally-visible promise made by one of
the five public surfaces (API / SCHEMA / EVENT / CAPABILITY / TOOL). Once a
contract is ``FROZEN`` it may not change silently: any modification must bump
the version and be documented by an ADR (Architecture Decision Record).

This module is intentionally dependency-free (standard library only) so it can
be imported from any layer without violating the architecture guard.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

__all__ = [
    "ContractStatus",
    "ContractSurface",
    "ALL_SURFACES",
    "Contract",
]


class ContractStatus(str, Enum):
    """Lifecycle status of a public contract."""

    FROZEN = "FROZEN"
    DRAFT = "DRAFT"
    DEPRECATED = "DEPRECATED"


class ContractSurface(str, Enum):
    """The five public surfaces that must each have a registered contract."""

    API = "API"
    SCHEMA = "SCHEMA"
    EVENT = "EVENT"
    CAPABILITY = "CAPABILITY"
    TOOL = "TOOL"


# Every public surface that must be covered by a frozen contract.
ALL_SURFACES: List[ContractSurface] = list(ContractSurface)

# Default deprecation window granted when a breaking (major) change is made to
# a frozen contract. Documented in the T064 ADR.
DEFAULT_DEPRECATION_WINDOW = "180d"


@dataclass
class Contract:
    """A single public contract (frozen at 1.0.0 for the T064 freeze).

    Fields (per T064 spec):
        name         — unique contract identifier (one per public surface).
        version      — SemVer string, default ``"1.0.0"``.
        status       — ``FROZEN`` | ``DRAFT`` | ``DEPRECATED``.
        surface      — ``API`` | ``SCHEMA`` | ``EVENT`` | ``CAPABILITY`` | ``TOOL``.
        compatibility— backward-compatible-until promise (e.g. ``"2.0.0"``).
        evidence_ref — reference to the conformance evidence / ADR.
    """

    name: str
    version: str = "1.0.0"
    status: ContractStatus = ContractStatus.DRAFT
    surface: ContractSurface = ContractSurface.API
    compatibility: str = ""
    evidence_ref: str = ""

    def __post_init__(self) -> None:
        # Normalize enum-typed fields so callers may pass strings.
        if not isinstance(self.status, ContractStatus):
            self.status = ContractStatus(self.status)
        if not isinstance(self.surface, ContractSurface):
            self.surface = ContractSurface(self.surface)
        self._validate_version()

    def _validate_version(self) -> None:
        parts = self.version.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(
                f"contract {self.name!r} has invalid SemVer version {self.version!r}; "
                "expected MAJOR.MINOR.PATCH"
            )

    @property
    def major(self) -> int:
        """Major version component (used to detect breaking changes)."""
        return int(self.version.split(".")[0])

    @property
    def is_frozen(self) -> bool:
        return self.status is ContractStatus.FROZEN
