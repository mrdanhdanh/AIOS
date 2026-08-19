"""Typed contracts with version metadata and compatibility checking.

A *contract* is a named interface with a required semver range.  The
compatibility checker verifies that a provided version satisfies the required
range.

Example::

    from aios.core.contracts import Contract, ContractError, check_compatibility

    c = Contract(name="storage", version_range=">=1.0.0,<2.0.0")
    check_compatibility(c, "1.5.0")   # OK
    check_compatibility(c, "2.0.0")   # raises ContractError
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .version import SemVer, VersionError

__all__ = ["Contract", "ContractError", "check_compatibility"]


class ContractError(Exception):
    """Raised when contract compatibility check fails."""


@dataclass(frozen=True)
class VersionRange:
    """A semver range with inclusive lower bound and exclusive upper bound.

    Format: ``>=MAJOR.MINOR.PATCH,<MAJOR.MINOR.PATCH``
    """

    min_version: SemVer
    max_version: SemVer

    def __post_init__(self) -> None:  # noqa: D105
        if self.min_version >= self.max_version:
            raise ContractError(
                f"min_version {self.min_version} must be < max_version {self.max_version}"
            )

    def contains(self, version: SemVer) -> bool:
        """Return True if *version* falls within this range."""
        return self.min_version <= version < self.max_version


_RANGE_RE = re.compile(
    r"^>=(?P<min>[0-9]+\.[0-9]+\.[0-9]+)"
    r"(?:-(?P<min_pre>[a-zA-Z0-9.\-]+))?"
    r",<(?P<max>[0-9]+\.[0-9]+\.[0-9]+)"
    r"(?:-(?P<max_pre>[a-zA-Z0-9.\-]+))?$"
)


def _parse_range(range_str: str) -> VersionRange:
    """Parse ``>=X.Y.Z,<A.B.C`` into a :class:`VersionRange`."""
    m = _RANGE_RE.match(range_str.strip())
    if not m:
        raise ContractError(f"Invalid version range: {range_str!r}")
    min_str = m.group("min")
    if m.group("min_pre"):
        min_str += f"-{m.group('min_pre')}"
    max_str = m.group("max")
    if m.group("max_pre"):
        max_str += f"-{m.group('max_pre')}"
    return VersionRange(
        min_version=SemVer.parse(min_str),
        max_version=SemVer.parse(max_str),
    )


@dataclass(frozen=True)
class Contract:
    """A named contract with a required version range.

    Examples::

        Contract(name="storage", version_range=">=1.0.0,<2.0.0")
        Contract(name="llm", version_range=">=0.1.0,<1.0.0")
    """

    name: str
    version_range: str
    description: str = ""

    def __post_init__(self) -> None:  # noqa: D105
        # Validate the range string eagerly.
        _parse_range(self.version_range)

    @property
    def range(self) -> VersionRange:
        """Parsed :class:`VersionRange`."""
        return _parse_range(self.version_range)

    def is_satisfied_by(self, version_str: str) -> bool:
        """Return True if *version_str* satisfies this contract."""
        try:
            v = SemVer.parse(version_str)
        except VersionError:
            return False
        return self.range.contains(v)


def check_compatibility(
    contract: Contract,
    provided_version: str,
) -> None:
    """Verify that *provided_version* satisfies *contract*.

    Raises :class:`ContractError` if incompatible.
    """
    if not contract.is_satisfied_by(provided_version):
        raise ContractError(
            f"Contract '{contract.name}' requires {contract.version_range}, "
            f"but provided version is {provided_version}"
        )


def check_contracts(
    contracts: List[Contract],
    providers: dict[str, str],
) -> None:
    """Check multiple contracts against a {name: version} mapping.

    Raises :class:`ContractError` on the first failure.
    """
    for c in contracts:
        ver = providers.get(c.name)
        if ver is None:
            raise ContractError(
                f"No provider registered for contract '{c.name}'"
            )
        check_compatibility(c, ver)
