"""AIOS Upgrade Pipeline — Safe upgrade/migration engine.

Provides compatibility checking, backup, migration, dry-run, validation,
and rollback capabilities for safe AIOS upgrades.
"""

from aios.upgrade.backup import BackupEngine, BackupManifest
from aios.upgrade.compatibility import CompatibilityChecker, CompatibilityResult
from aios.upgrade.dryrun import DryRunEngine, DryRunResult
from aios.upgrade.manifest import UpgradeManifest, UpgradeStep
from aios.upgrade.migration import MigrationEngine, MigrationResult
from aios.upgrade.rollback import RollbackEngine, RollbackResult
from aios.upgrade.validation import ValidationResult, ValidationPipeline
from aios.upgrade.migration_plan import (
    MigrationPlan,
    MigrationStep,
    MigrationEngine as MigrationPlanEngine,
    MigrationReport,
    MigrationError,
    MigrationPhase,
    StepEvidence,
    sample_durable_migration_step,
    make_durable_migration_plan,
    hash_state,
)

__all__ = [
    "UpgradeManifest",
    "UpgradeStep",
    "CompatibilityChecker",
    "CompatibilityResult",
    "BackupEngine",
    "BackupManifest",
    "MigrationEngine",
    "MigrationResult",
    "DryRunEngine",
    "DryRunResult",
    "ValidationPipeline",
    "ValidationResult",
    "RollbackEngine",
    "RollbackResult",
    "MigrationPlan",
    "MigrationStep",
    "MigrationPlanEngine",
    "MigrationReport",
    "MigrationError",
    "MigrationPhase",
    "StepEvidence",
    "sample_durable_migration_step",
    "make_durable_migration_plan",
    "hash_state",
]
