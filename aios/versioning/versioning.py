"""Version + Compatibility Baseline — semver policy, matrix, deprecation (T084).

Canonical versioning policy for AIOS 1.x:

    VersionPolicy
    ├── scheme: semver
    ├── breaking -> MAJOR
    ├── compatible -> MINOR
    ├── deprecation_window
    └── evidence_ref

Safety properties (all fail-closed / provenance / deterministic):
* No silent breaking — breaking -> MAJOR + ADR + deprecation window.
* Deprecation notice — a deprecated surface must be announced in advance.
* Evidence required — every version policy decision carries provenance.
* Deterministic — the same change type always yields the same version bump.
* No parallel versioning — uses the Contract (T064) + ADR convention.

Integration: imports ``aios.contracts.contract`` (T064) for the deprecation
window default and surface enumeration. No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aios.contracts.contract import DEFAULT_DEPRECATION_WINDOW


class ChangeType(str, Enum):
    """Classification of a proposed version change."""

    BREAKING = "breaking"
    COMPATIBLE = "compatible"
    FIX = "fix"


class VersionBump(str, Enum):
    """The SemVer component that a change type must bump."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@dataclass
class VersionPolicy:
    """The versioning policy baseline (ADR-backed)."""

    scheme: str = "semver"
    deprecation_window: str = DEFAULT_DEPRECATION_WINDOW
    baseline_version: str = "1.0.0"
    adr_ref: str = "ADR-Compatibility"
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scheme": self.scheme,
            "deprecation_window": self.deprecation_window,
            "baseline_version": self.baseline_version,
            "adr_ref": self.adr_ref,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class VersionChange:
    """A proposed change to be classified by the policy engine."""

    change_type: ChangeType
    description: str = ""
    has_adr: bool = False
    has_deprecation_notice: bool = False
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "description": self.description,
            "has_adr": self.has_adr,
            "has_deprecation_notice": self.has_deprecation_notice,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class VersionDecision:
    """The deterministic, fail-closed result of classifying a change."""

    change_type: ChangeType
    bump: VersionBump
    allowed: bool
    reason: str
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "bump": self.bump.value,
            "allowed": self.allowed,
            "reason": self.reason,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class VersionBaseline:
    """The official compatibility baseline document (ADR reference)."""

    baseline_version: str = "1.0.0"
    adr_ref: str = "ADR-Compatibility"
    surfaces: tuple[str, ...] = ("API", "SCHEMA", "EVENT", "CAPABILITY", "TOOL")
    deprecation_window: str = DEFAULT_DEPRECATION_WINDOW
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_version": self.baseline_version,
            "adr_ref": self.adr_ref,
            "surfaces": list(self.surfaces),
            "deprecation_window": self.deprecation_window,
            "evidence_ref": self.evidence_ref,
        }


class CompatibilityMatrix:
    """Defines how AIOS versions relate for backward compatibility.

    Rule (T084): a target version is backward-compatible with a base version
    when they share the same MAJOR component and ``target >= base``. A different
    MAJOR means a breaking release that must go through the deprecation window.
    """

    @staticmethod
    def _parse(version: str) -> tuple[int, int, int]:
        m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
        if not m:
            raise ValueError(f"invalid SemVer version: {version!r}")
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    @classmethod
    def is_compatible(cls, base: str, target: str) -> bool:
        """True when ``target`` is backward-compatible with ``base`` (same major)."""
        b_major, b_minor, b_patch = cls._parse(base)
        t_major, t_minor, t_patch = cls._parse(target)
        if t_major != b_major:
            return False
        return (t_minor, t_patch) >= (b_minor, b_patch)

    @classmethod
    def is_breaking(cls, base: str, target: str) -> bool:
        """True when moving base -> target crosses a MAJOR boundary."""
        return cls._parse(target)[0] != cls._parse(base)[0]


class VersionPolicyEngine:
    """Deterministic, fail-closed classifier of version changes."""

    def __init__(self, policy: VersionPolicy | None = None) -> None:
        self.policy = policy or VersionPolicy()

    # -- deterministic bump mapping ------------------------------------------

    @staticmethod
    def _bump_for(change_type: ChangeType) -> VersionBump:
        """Same change type -> same bump (deterministic)."""
        return {
            ChangeType.BREAKING: VersionBump.MAJOR,
            ChangeType.COMPATIBLE: VersionBump.MINOR,
            ChangeType.FIX: VersionBump.PATCH,
        }[change_type]

    def decide(self, change: VersionChange) -> VersionDecision:
        """Classify a change into a fail-closed version decision.

        * BREAKING -> MAJOR, but only allowed with an ADR + deprecation notice.
        * COMPATIBLE -> MINOR.
        * FIX -> PATCH.
        Every decision carries provenance (evidence_ref).
        """
        bump = self._bump_for(change.change_type)
        if change.change_type is ChangeType.BREAKING:
            allowed = change.has_adr and change.has_deprecation_notice
            reason = (
                "breaking change requires MAJOR + ADR + deprecation window"
                if allowed
                else "BLOCKED: breaking change without ADR and/or deprecation notice"
            )
        else:
            allowed = True
            reason = f"{change.change_type.value} change -> {bump.value} bump"
        return VersionDecision(
            change_type=change.change_type,
            bump=bump,
            allowed=allowed,
            reason=reason,
            evidence_ref=change.evidence_ref,
        )

    @staticmethod
    def bump_version(current: str, bump: VersionBump) -> str:
        """Return the next version after applying ``bump`` to ``current``."""
        major, minor, patch = CompatibilityMatrix._parse(current)
        if bump is VersionBump.MAJOR:
            return f"{major + 1}.0.0"
        if bump is VersionBump.MINOR:
            return f"{major}.{minor + 1}.0"
        return f"{major}.{minor}.{patch + 1}"

    def provenance_complete(self, change: VersionChange) -> bool:
        """A version change is only provenanced when it carries an evidence ref."""
        return bool(change.evidence_ref)

    def baseline_hash(self, baseline: VersionBaseline | None = None) -> str:
        """Deterministic hash of the baseline document (provenance anchor)."""
        data = json.dumps(
            (baseline or VersionBaseline()).to_dict(), sort_keys=True
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
