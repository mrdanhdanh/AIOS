"""Version + Compatibility Baseline (TASK-084, M12).

Public versioning policy + compatibility baseline for AIOS 1.x. This module is
the canonical reference for every later compatibility task (T085-T088). It is a
*versioning policy + baseline*, not a new runtime feature (built on the Contract
Freeze T064).

Fail-closed: a breaking change without an ADR + deprecation window is rejected
(never silent). Deterministic: the same change type always yields the same
version bump. Every policy decision carries provenance (T001 Rule 5).
"""

from aios.versioning.versioning import (
    ChangeType,
    CompatibilityMatrix,
    VersionBaseline,
    VersionBump,
    VersionChange,
    VersionDecision,
    VersionPolicy,
    VersionPolicyEngine,
)

__all__ = [
    "ChangeType",
    "CompatibilityMatrix",
    "VersionBaseline",
    "VersionBump",
    "VersionChange",
    "VersionDecision",
    "VersionPolicy",
    "VersionPolicyEngine",
]
