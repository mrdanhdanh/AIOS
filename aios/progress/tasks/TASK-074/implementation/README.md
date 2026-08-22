# TASK-074 — Implementation

This directory is a pointer to the real implementation. TASK-074 extends the
existing `aios/upgrade` package; no new runtime subsystem was created.

## Real module
- `aios/upgrade/migration_plan.py`
  - `MigrationPlan` — ordered, reversible plan (`from_version`, `to_version`,
    `steps`, `dry_run_supported`, `evidence_ref`).
  - `MigrationStep` — `{id, up, down, verify}` (every step reversible).
  - `MigrationEngine` — `detect_current_version`, `select_plan`, `run`
    (ordered, fail-closed verify, dry-run no-mutate), `rollback`, `migrate`.
  - `MigrationReport` / `StepEvidence` — provenance with content hashes.
  - `sample_durable_migration_step` / `make_durable_migration_plan` — safe
    durable-state migration (T066 / `aios.goal_durability`), no data loss.
  - `hash_state` — deterministic state hash.

## Integration points (downward/peer only, no `agents/`)
- `aios/upgrade/manifest.py` — `MigrationPlan.to_manifest()` → `UpgradeManifest`.
- `aios/goal_durability/contracts.py` — `DurableCheckpoint` (durable state).
- `aios/harness/verification.py` — `VerificationPipeline`, `Verdict` (T032).

## Tests
- `aios/upgrade/tests/test_migration_plan.py`
- Run: `python -m pytest aios/upgrade -q`
