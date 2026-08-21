"""Compatibility checker — verifies upgrade feasibility before mutation.

AC-020-02: Compatibility checked before mutation.
AC-020-03: Dependencies resolved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CompatibilityResult(str, Enum):
    """Result of compatibility check."""
    COMPATIBLE = "compatible"
    MIGRATION_REQUIRED = "migration_required"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass
class CompatibilityCheck:
    """Result of a single compatibility check."""

    name: str
    result: CompatibilityResult
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "result": self.result.value,
            "detail": self.detail,
        }


class CompatibilityChecker:
    """Checks compatibility between source and target versions.

    AC-020-02: Compatibility checked before mutation.
    UNKNOWN is not treated as compatible (fail-closed).
    """

    def check_version(self, source: str, target: str) -> CompatibilityCheck:
        """Check version compatibility."""
        if source == target:
            return CompatibilityCheck(
                name="version",
                result=CompatibilityResult.COMPATIBLE,
                detail="Same version — no upgrade needed",
            )
        # Parse major.minor.patch
        try:
            src_parts = [int(x) for x in source.split(".")]
            tgt_parts = [int(x) for x in target.split(".")]
        except (ValueError, AttributeError):
            return CompatibilityCheck(
                name="version",
                result=CompatibilityResult.UNKNOWN,
                detail=f"Cannot parse versions: {source} → {target}",
            )

        if len(src_parts) < 2 or len(tgt_parts) < 2:
            return CompatibilityCheck(
                name="version",
                result=CompatibilityResult.UNKNOWN,
                detail="Version format too short",
            )

        if tgt_parts[0] > src_parts[0]:
            return CompatibilityCheck(
                name="version",
                result=CompatibilityResult.MIGRATION_REQUIRED,
                detail=f"Major version bump: {source} → {target}",
            )
        if tgt_parts[1] > src_parts[1]:
            return CompatibilityCheck(
                name="version",
                result=CompatibilityResult.MIGRATION_REQUIRED,
                detail=f"Minor version bump: {source} → {target}",
            )
        if tgt_parts[2] > src_parts[2]:
            return CompatibilityCheck(
                name="version",
                result=CompatibilityResult.COMPATIBLE,
                detail=f"Patch version bump: {source} → {target}",
            )
        return CompatibilityCheck(
            name="version",
            result=CompatibilityResult.COMPATIBLE,
            detail="Version downgrade or same",
        )

    def check_contracts(
        self,
        source_contracts: dict[str, str],
        target_contracts: dict[str, str],
    ) -> CompatibilityCheck:
        """Check contract version compatibility."""
        all_names = set(source_contracts) | set(target_contracts)
        breaking = []
        for name in all_names:
            src = source_contracts.get(name)
            tgt = target_contracts.get(name)
            if src is None:
                continue  # New contract — compatible
            if tgt is None:
                breaking.append(f"{name} removed")
                continue
            if src != tgt:
                breaking.append(f"{name}: {src} → {tgt}")

        if breaking:
            return CompatibilityCheck(
                name="contracts",
                result=CompatibilityResult.MIGRATION_REQUIRED,
                detail=f"Contract changes: {'; '.join(breaking)}",
            )
        return CompatibilityCheck(
            name="contracts",
            result=CompatibilityResult.COMPATIBLE,
            detail="All contracts compatible",
        )

    def check_dependencies(
        self,
        required: dict[str, str],
        available: dict[str, str],
    ) -> CompatibilityCheck:
        """Check dependency resolution.

        AC-020-03: Dependencies resolved.
        """
        missing = []
        version_mismatch = []
        for name, required_ver in required.items():
            if name not in available:
                missing.append(name)
            elif available[name] != required_ver:
                version_mismatch.append(f"{name}: need {required_ver}, have {available[name]}")

        issues = missing + version_mismatch
        if issues:
            return CompatibilityCheck(
                name="dependencies",
                result=CompatibilityResult.INCOMPATIBLE,
                detail=f"Dependency issues: {'; '.join(issues)}",
            )
        return CompatibilityCheck(
            name="dependencies",
            result=CompatibilityResult.COMPATIBLE,
            detail="All dependencies satisfied",
        )

    def check_all(
        self,
        source_version: str,
        target_version: str,
        source_contracts: dict[str, str] | None = None,
        target_contracts: dict[str, str] | None = None,
        required_deps: dict[str, str] | None = None,
        available_deps: dict[str, str] | None = None,
    ) -> CompatibilityResult:
        """Run all compatibility checks and return overall result.

        UNKNOWN is fail-closed: if any check is UNKNOWN, overall is UNKNOWN.
        """
        checks = [self.check_version(source_version, target_version)]

        if source_contracts is not None and target_contracts is not None:
            checks.append(self.check_contracts(source_contracts, target_contracts))

        if required_deps is not None and available_deps is not None:
            checks.append(self.check_dependencies(required_deps, available_deps))

        results = [c.result for c in checks]

        if CompatibilityResult.INCOMPATIBLE in results:
            return CompatibilityResult.INCOMPATIBLE
        if CompatibilityResult.UNKNOWN in results:
            return CompatibilityResult.UNKNOWN
        if CompatibilityResult.MIGRATION_REQUIRED in results:
            return CompatibilityResult.MIGRATION_REQUIRED
        return CompatibilityResult.COMPATIBLE
