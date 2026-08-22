# Implementation — TASK-085

Module: `aios/migration/`
- `migration.py` — `MigrationStep`, `MigrationPlan`, `MigrationState`,
  `DryRunResult`, `MigrationResult`, `RollbackResult`, `MigrationRunner`.
- `tests/test_migration.py` — 8 tests (Test Matrix).

Tích hợp: import `aios.upgrade.migration_plan` (T074, `MigrationPhase`/`MigrationStep`),
`aios.harness.verification` (T032, `Verdict`), `aios.versioning.versioning` (T084,
`VersionBaseline`) — không rewrite.
