# TASK-074 — Test

## How to verify
```powershell
cd d:\AIOS
python -m pytest aios/upgrade -q
```

## What is covered
File: `aios/upgrade/tests/test_migration_plan.py`

| Area | Test class |
|------|------------|
| Version detect → correct plan | `TestVersionDetection` |
| Ordered execution | `TestOrderedExecution` |
| Verify FAIL → not applied (fail-closed) | `TestVerifyFailClosed` |
| Step has `down` → rollback succeeds | `TestRollback` |
| Dry-run → no mutate | `TestDryRun` |
| Migrate durable state → no data loss (T066) | `TestDurableStateMigration` |
| Same plan + state → same result (deterministic) | `TestDeterministic` |
| Reversible enforcement + evidence provenance | `TestSafetyProperties` |
| Peer integration with `aios.upgrade` + harness | `TestPeerIntegration` |

## Result
- 64 passed (62 pre-existing upgrade tests + 2 new files' tests).
- No existing upgrade tests broken.
