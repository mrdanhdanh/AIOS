# TASK-074 — Breakdown

## Subtasks
1. **Model** — `MigrationStep` (id, up, down, verify) and `MigrationPlan`
   (from_version, to_version, steps, dry_run_supported, evidence_ref).
   - File: `aios/upgrade/migration_plan.py`
2. **Engine** — `MigrationEngine.detect_current_version`, `select_plan`,
   `run` (ordered, fail-closed verify, dry-run no-mutate), `rollback`
   (reverse order), `migrate` convenience.
   - File: `aios/upgrade/migration_plan.py`
3. **Harness integration** — each step `verify` runs through
   `aios.harness.verification.VerificationPipeline` → `Verdict` + evidence.
4. **Durable integration** — `sample_durable_migration_step` migrates a
   `DurableCheckpoint.goal_state` (adds `schema_version`) with no data loss
   and full reversibility.
5. **Peer integration** — `MigrationPlan.to_manifest()` → `UpgradeManifest`.
6. **Evidence** — `StepEvidence` per verify/apply/rollback with content hash.
7. **Tests** — `aios/upgrade/tests/test_migration_plan.py` covering all ACs
   and Test Matrix rows.
8. **Exports** — add new symbols to `aios/upgrade/__init__.py`.
9. **Artifacts** — 9 lifecycle artifacts in `aios/progress/tasks/TASK-074/`.

## Verification
- `python -m pytest aios/upgrade -q` → all pass (64 tests).
