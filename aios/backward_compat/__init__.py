"""Backward Compatibility (TASK-086, M12).

Guarantees that an AIOS 1.x system keeps serving consumers written for 1.0
without breaking (API / schema / event surfaces unchanged in a breaking way).
Built on the Contract Freeze (T064), the Version + Compatibility Baseline (T084)
and the Migration 1.0->1.1 (T085).

Fail-closed: a breaking change against a 1.0 consumer is BLOCKED (must go through
MAJOR + deprecation, T084). Deterministic: same surface + version -> same result.
Evidence: every compat check carries provenance (T001 Rule 5).
"""

from aios.backward_compat.backward import (
    BackwardCompatChecker,
    CompatCheck,
    CompatResult,
    CompatSurface,
    CompatSuiteResult,
    CompatTestSuite,
)

__all__ = [
    "BackwardCompatChecker",
    "CompatCheck",
    "CompatResult",
    "CompatSurface",
    "CompatSuiteResult",
    "CompatTestSuite",
]
