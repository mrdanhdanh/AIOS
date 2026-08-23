# TASK-020 Implementation — Upgrade Pipeline

Implementation lives in `aios/upgrade/` (M4 Platform Edition — Upgrade/Migration).

```
aios/upgrade/
  manifest.py       # Upgrade manifest (version, contracts, migrations, rollback)
  compatibility.py  # Compatibility checker (contract/schema version)
  backup.py         # Backup/snapshot (certified state)
  migration.py      # Migration engine (deterministic, idempotent, version-aware)
  migration_plan.py # Migration plan (resolve → plan)
  dryrun.py         # Dry-run engine (no side effects, deterministic)
  validation.py     # Validation pipeline (contract/schema/registry/arch/health)
  rollback.py       # Rollback engine (restore certified state, evidence)
  __init__.py       # re-exports
  tests/
    test_manifest.py
    test_compatibility.py
    test_migration.py
    test_dryrun.py
    test_rollback.py
```

Flow: `Resolve → Backup → Migrate → Validate → Rollback` + `dry-run` (deterministic, no side effects). Migration failure → rollback to certified state (fail-closed, evidence).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
