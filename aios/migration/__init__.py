"""Migration 1.0 -> 1.1 (TASK-085, M12).

Version migration tooling: detect a 1.0 system, plan an ordered + reversible
migration to 1.1, dry-run without mutating, apply with fail-closed verification,
and roll back to 1.0. Built on the Upgrade/Migration pipeline (T074), the Version
+ Compatibility Baseline (T084) and the Harness verification pipeline (T032).

Fail-closed: verify FAIL -> never apply. Reversible: every step has a ``down``.
Evidence: every step records provenance (T001 Rule 5). Deterministic: same plan
+ state -> same result. No data loss: state migration is durable (T066).
"""

from aios.migration.migration import (
    MigrationError,
    MigrationPlan,
    MigrationResult,
    MigrationRunner,
    MigrationState,
    MigrationStep,
    RollbackResult,
    DryRunResult,
)

__all__ = [
    "MigrationError",
    "MigrationPlan",
    "MigrationResult",
    "MigrationRunner",
    "MigrationState",
    "MigrationStep",
    "RollbackResult",
    "DryRunResult",
]
