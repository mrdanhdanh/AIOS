# TASK-020 — Upgrade Pipeline

## Objective
Build a safe upgrade/migration pipeline with compatibility checking, backup, migration, validation, dry-run, and rollback capabilities. Ensures certified state is never lost during upgrades.

## Scope
### In scope
- Upgrade manifest schema and parsing
- Compatibility checker (version, contract, schema, dependency)
- Backup/snapshot creation before migration
- Migration engine (deterministic, idempotent, version-aware)
- Dry-run simulation (no side effects)
- Validation pipeline (post-migration checks)
- Rollback engine (restores certified state)
- Evidence creation for upgrade/rollback events
- CLI interface for upgrade operations

### Out of scope
- Actual data migration between database versions
- Network-based distributed upgrades (M7)
- Plugin-specific migration scripts
- UI for upgrade management

## Deliverables
- `aios/upgrade/__init__.py` — public API
- `aios/upgrade/manifest.py` — upgrade manifest schema
- `aios/upgrade/compatibility.py` — compatibility checker
- `aios/upgrade/backup.py` — backup/snapshot engine
- `aios/upgrade/migration.py` — migration engine
- `aios/upgrade/dryrun.py` — dry-run simulation
- `aios/upgrade/validation.py` — post-migration validation
- `aios/upgrade/rollback.py` — rollback engine
- `aios/upgrade/tests/` — comprehensive tests

## Acceptance Criteria
- AC-020-01: Upgrade has preflight
- AC-020-02: Compatibility checked before mutation
- AC-020-03: Dependencies resolved
- AC-020-04: Backup/snapshot exists before migration
- AC-020-05: Dry-run creates no side effects
- AC-020-06: Dry-run deterministic
- AC-020-07: Migration has validation
- AC-020-08: Migration failure auto-rollback per policy
- AC-020-09: Certified state restored accurately
- AC-020-10: No bypass of Policy/Permission
- AC-020-11: Evidence for upgrade and rollback
- AC-020-12: M0–M3 regression PASS

## Dependencies
- TASK-019 (VS Code Extension)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
