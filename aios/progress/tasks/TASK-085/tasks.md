# Task Breakdown — TASK-085

- [x] MigrationStep (id, up, down, verify, evidence_ref) — reversible.
- [x] MigrationPlan (from 1.0.0, to 1.1.0, steps, dry_run_supported).
- [x] MigrationState (version, data) + snapshot (no mutate).
- [x] MigrationRunner.detect (1.0).
- [x] MigrationRunner.plan (ordered, reversible).
- [x] MigrationRunner.dry_run (no mutate).
- [x] MigrationRunner.apply (verify FAIL → no apply, fail-closed).
- [x] MigrationRunner.rollback (to 1.0).
- [x] MigrationResult.state (no data loss) + RollbackResult.
- [x] Tests 8 cases (Test Matrix).
- [x] Tích hợp Upgrade (T074) + Version (T084) + Harness (T032).
