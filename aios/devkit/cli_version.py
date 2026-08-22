"""CLI versioning policy for AIOS Developer Experience (TASK-071).

Encodes the DX safety rule: a *breaking* CLI change (removing or renaming a
stable subcommand) MUST be accompanied by a version bump and a deprecation
window. This is fail-closed — if a breaking change is detected without a bump
the policy raises :class:`CliStabilityError`.
"""

from __future__ import annotations

from typing import Iterable

from aios.devkit.errors import CliStabilityError, CliVersionBumpRequired
from aios.core.version import SemVer, VersionError

# The version of the public `aiagent` CLI surface. Bump the MAJOR part whenever
# a stable subcommand is removed or its signature changes incompatibly.
CLI_VERSION = "1.0.0"


def is_breaking_change(baseline: Iterable[str], current: Iterable[str]) -> list[str]:
    """Return the list of stable commands removed between two command sets."""
    base = set(baseline)
    cur = set(current)
    return sorted(base - cur)


def require_version_bump_if_breaking(
    removed: Iterable[str],
    old_version: str,
    new_version: str,
) -> None:
    """Raise if a breaking change occurs without a version bump.

    A *bump* means the new version is strictly greater than the old version
    under SemVer ordering. If commands were removed but the version did not
    advance, :class:`CliVersionBumpRequired` is raised (fail-closed).
    """
    removed = list(removed)
    if not removed:
        return
    try:
        bumped = SemVer.parse(new_version) > SemVer.parse(old_version)
    except VersionError as exc:  # pragma: no cover - defensive
        raise CliStabilityError(
            f"Invalid CLI version: {exc}",
            cause="CLI_VERSION is not valid SemVer.",
            fix_hint="Set CLI_VERSION to a valid MAJOR.MINOR.PATCH string.",
        ) from exc
    if not bumped:
        raise CliVersionBumpRequired(
            f"Breaking CLI change detected: removed {removed} without a version bump.",
            cause=(
                "Stable subcommand(s) were removed/renamed but CLI_VERSION "
                f"({old_version}) was not advanced."
            ),
            fix_hint=(
                "Bump CLI_VERSION (e.g. to a new MAJOR) and add a deprecation "
                "window before removing the command."
            ),
            context={"removed": removed, "old_version": old_version, "new_version": new_version},
        )


class CliVersionPolicy:
    """Validates CLI stability against the breaking-change rule."""

    def __init__(self, current_version: str = CLI_VERSION) -> None:
        self.current_version = current_version

    def assert_stable(
        self,
        baseline_commands: Iterable[str],
        current_commands: Iterable[str],
        baseline_version: str | None = None,
    ) -> list[str]:
        """Assert no breaking change without a version bump.

        Returns the list of removed commands (empty when stable). Raises
        :class:`CliVersionBumpRequired` when a breaking change is unaccompanied
        by a version bump.
        """
        removed = is_breaking_change(baseline_commands, current_commands)
        if not removed:
            return removed
        old_version = baseline_version or self.current_version
        require_version_bump_if_breaking(removed, old_version, self.current_version)
        return removed

    def deprecate(self, command: str, since_version: str, remove_in: str) -> dict:
        """Record a deprecation window for a command (DX safety rule)."""
        return {
            "command": command,
            "since_version": since_version,
            "remove_in": remove_in,
            "status": "deprecated",
        }
