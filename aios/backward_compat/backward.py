"""Backward Compatibility — API / schema / event compat guarantee (T086).

Canonical compat contract:

    CompatCheck
    ├── surface: API | SCHEMA | EVENT
    ├── consumer_version: 1.0
    ├── provider_version: 1.x
    ├── compatible: bool
    └── evidence_ref

Safety properties (all fail-closed / deprecation / evidence / deterministic):
* Fail-closed compat — a breaking change against a 1.0 consumer is BLOCKED.
* Deprecation required — to break, it must go through T084 (MAJOR + window).
* Evidence required — every compat check carries provenance (T001 Rule 5).
* Deterministic — same surface + version -> same result.
* No parallel compat system — uses Contract (T064) + Version (T084).

Integration: imports ``aios.contracts.contract`` (T064) for the surface
enumeration and ``aios.versioning.versioning`` (T084) for the compatibility
matrix. No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aios.contracts.contract import ContractSurface
from aios.versioning.versioning import CompatibilityMatrix

CONSUMER_VERSION = "1.0.0"


class CompatSurface(str, Enum):
    """The three behavioral surfaces locked by the compat test suite."""

    API = "API"
    SCHEMA = "SCHEMA"
    EVENT = "EVENT"

    @classmethod
    def from_contract_surface(cls, surface: ContractSurface) -> "CompatSurface":
        return cls(surface.value)


@dataclass
class CompatCheck:
    """A single backward-compatibility check."""

    surface: CompatSurface
    provider_version: str
    consumer_version: str = CONSUMER_VERSION
    breaking: bool = False
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface.value,
            "consumer_version": self.consumer_version,
            "provider_version": self.provider_version,
            "breaking": self.breaking,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class CompatResult:
    """The fail-closed result of a single compat check."""

    surface: CompatSurface
    consumer_version: str
    provider_version: str
    compatible: bool
    blocked: bool
    reason: str
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface.value,
            "consumer_version": self.consumer_version,
            "provider_version": self.provider_version,
            "compatible": self.compatible,
            "blocked": self.blocked,
            "reason": self.reason,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class CompatSuiteResult:
    """Result of running the full compat test suite (locks 1.0 behavior)."""

    passed: bool
    results: list[CompatResult] = field(default_factory=list)
    blocked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "blocked": self.blocked,
            "results": [r.to_dict() for r in self.results],
        }


class BackwardCompatChecker:
    """Fail-closed backward-compatibility checker."""

    def check(self, chk: CompatCheck) -> CompatResult:
        """Evaluate a single compat check.

        * A breaking change against a 1.0 consumer is BLOCKED (must be MAJOR +
          deprecation per T084). It is never silently accepted.
        * A non-breaking change on a compatible version is compatible.
        """
        if chk.breaking:
            # Breaking against 1.0 consumer -> BLOCK (fail-closed). The only
            # allowed path is a MAJOR bump with a deprecation window (T084).
            return CompatResult(
                surface=chk.surface,
                consumer_version=chk.consumer_version,
                provider_version=chk.provider_version,
                compatible=False,
                blocked=True,
                reason="BLOCKED: breaking change against 1.0 consumer; "
                       "must go through MAJOR + deprecation (T084)",
                evidence_ref=chk.evidence_ref,
            )
        # Non-breaking: compatible iff the provider version is backward
        # compatible with the 1.0 consumer (same major, >= base).
        compatible = CompatibilityMatrix.is_compatible(
            chk.consumer_version, chk.provider_version
        )
        return CompatResult(
            surface=chk.surface,
            consumer_version=chk.consumer_version,
            provider_version=chk.provider_version,
            compatible=compatible,
            blocked=not compatible,
            reason=(
                "compatible" if compatible
                else "provider version not backward-compatible with 1.0 consumer"
            ),
            evidence_ref=chk.evidence_ref,
        )

    def run_suite(self, checks: list[CompatCheck]) -> CompatSuiteResult:
        """Run the full compat test suite. Any FAIL/BLOCK -> suite fails."""
        results = [self.check(c) for c in checks]
        blocked = any(r.blocked for r in results)
        passed = (not blocked) and all(r.compatible for r in results)
        return CompatSuiteResult(passed=passed, results=results, blocked=blocked)

    def provenance_complete(self, chk: CompatCheck) -> bool:
        return bool(chk.evidence_ref)

    def suite_hash(self, checks: list[CompatCheck]) -> str:
        """Deterministic hash of the suite (same checks -> same hash)."""
        data = json.dumps(
            [c.to_dict() for c in checks], sort_keys=True
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()


class CompatTestSuite:
    """A locked set of 1.0 behavior checks (the compat test suite).

    Wraps ``BackwardCompatChecker`` with a fixed collection of checks that lock
    the 1.0 contract for the API / SCHEMA / EVENT surfaces. Running the suite is
    fail-closed: any BLOCK/FAIL prevents a DONE (T086).
    """

    def __init__(self, checks: list[CompatCheck] | None = None) -> None:
        self._checker = BackwardCompatChecker()
        self.checks = list(checks) if checks else []

    def add(self, check: CompatCheck) -> None:
        self.checks.append(check)

    def run(self) -> CompatSuiteResult:
        return self._checker.run_suite(self.checks)

    def provenance_complete(self) -> bool:
        return all(self._checker.provenance_complete(c) for c in self.checks)

    def suite_hash(self) -> str:
        return self._checker.suite_hash(self.checks)
