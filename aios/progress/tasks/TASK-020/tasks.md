# TASK-020 — Breakdown

1. Create `aios/upgrade/__init__.py` — public API
2. Create `aios/upgrade/manifest.py` — upgrade manifest schema
3. Create `aios/upgrade/compatibility.py` — compatibility checker
4. Create `aios/upgrade/backup.py` — backup/snapshot engine
5. Create `aios/upgrade/migration.py` — migration engine
6. Create `aios/upgrade/dryrun.py` — dry-run simulation
7. Create `aios/upgrade/validation.py` — post-migration validation
8. Create `aios/upgrade/rollback.py` — rollback engine
9. Create test files for all modules
10. Run full test suite + architecture gate
