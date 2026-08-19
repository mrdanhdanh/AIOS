"""Semantic versioning per SemVer 2.0.

Parse, compare, and validate ``MAJOR.MINOR.PATCH[-prerelease][+build]``
version strings.

Example::

    from aios.core.version import SemVer, VersionError

    v = SemVer.parse("1.2.3")
    assert v > SemVer.parse("1.2.2")
"""

from __future__ import annotations

import re
from functools import total_ordering
from typing import List, Optional, Tuple

__all__ = ["SemVer", "VersionError"]

# SemVer 2.0 regex (simplified — allows dot-separated numeric pre-release).
_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)"
    r"\.(?P<minor>0|[1-9]\d*)"
    r"\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    r"$"
)


class VersionError(Exception):
    """Raised when a version string is not valid SemVer 2.0."""


def _parse_pre_release(s: Optional[str]) -> Tuple[str, ...]:
    """Split a pre-release string into a comparable tuple of segments."""
    if not s:
        return ()
    return tuple(s.split("."))


def _compare_pre_release(
    a: Tuple[str, ...], b: Tuple[str, ...]
) -> int:
    """Compare two pre-release tuples per SemVer 2.0 rules.

    Rules:
    - Fewer segments < more segments (when all preceding segments equal).
    - Numeric segments compared as integers; strings compared lexically.
    - Numeric < string (numeric has lower precedence).
    """
    for x, y in zip(a, b):
        ax_is_num = x.isdigit()
        ay_is_num = y.isdigit()
        if ax_is_num and ay_is_num:
            cmp = int(x) - int(y)
        elif ax_is_num:
            cmp = -1  # numeric < string
        elif ay_is_num:
            cmp = 1
        else:
            cmp = (x > y) - (x < y)
        if cmp != 0:
            return cmp
    # All shared segments equal — shorter tuple wins.
    return len(a) - len(b)


@total_ordering
class SemVer:
    """Immutable semantic version.

    Examples::

        v = SemVer.parse("1.0.0-alpha.1")
        assert v.major == 1
        assert v < SemVer.parse("1.0.0")
    """

    __slots__ = ("major", "minor", "patch", "_prerelease", "_build")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: str = "",
        build: str = "",
    ) -> None:
        if major < 0 or minor < 0 or patch < 0:
            raise VersionError(
                f"Version components must be non-negative: {major}.{minor}.{patch}"
            )
        object.__setattr__(self, "major", major)
        object.__setattr__(self, "minor", minor)
        object.__setattr__(self, "patch", patch)
        object.__setattr__(self, "_prerelease", prerelease)
        object.__setattr__(self, "_build", build)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    @classmethod
    def parse(cls, version_str: str) -> SemVer:
        """Parse a SemVer 2.0 string.

        Raises :class:`VersionError` on invalid input.
        """
        m = _SEMVER_RE.match(version_str.strip())
        if not m:
            raise VersionError(f"Invalid semver string: {version_str!r}")
        return cls(
            major=int(m.group("major")),
            minor=int(m.group("minor")),
            patch=int(m.group("patch")),
            prerelease=m.group("prerelease") or "",
            build=m.group("build") or "",
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def prerelease(self) -> str:
        return self._prerelease

    @property
    def build(self) -> str:
        return self._build

    @property
    def is_prerelease(self) -> bool:
        return bool(self._prerelease)

    # ------------------------------------------------------------------
    # Comparison (build metadata is ignored per SemVer)
    # ------------------------------------------------------------------
    def _cmp_key(self) -> Tuple[int, int, int, Tuple[str, ...]]:
        return (
            self.major,
            self.minor,
            self.patch,
            _parse_pre_release(self._prerelease),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._cmp_key() == other._cmp_key()

    def __lt__(self, other: SemVer) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        a = self._cmp_key()
        b = other._cmp_key()
        # Compare numeric parts first.
        for x, y in zip(a[:3], b[:3]):
            if x != y:
                return x < y
        # Pre-release comparison.
        pre_a = a[3]
        pre_b = b[3]
        # A pre-release version has lower precedence than the associated
        # normal version (e.g. 1.0.0-alpha < 1.0.0).
        if pre_a and not pre_b:
            return True
        if not pre_a and pre_b:
            return False
        return _compare_pre_release(pre_a, pre_b) < 0

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self._prerelease:
            s += f"-{self._prerelease}"
        if self._build:
            s += f"+{self._build}"
        return s

    def __repr__(self) -> str:
        return f"SemVer({str(self)!r})"

    def __hash__(self) -> int:
        return hash(self._cmp_key())
