# TASK-003 — Test

## How to run
```
cd d:\AIOS
python -m pytest aios -q
```

## What is covered (78 new automated tests)

| Module | Tests | Coverage |
|--------|-------|----------|
| core/version | 14 | SemVer parsing, comparison, pre-release, edge cases |
| core/contracts | 10 | Contract creation, range parsing, compatibility checking |
| core/container | 12 | DI lifetimes (singleton/scoped/transient), thread safety, factories |
| core/events | 10 | Pub/sub, ordering, error handling, programmatic subscription |
| core/planner | 18 | Step transitions, plan operations, status tracking |
| core/smoke (updated) | 5 | Import smoke for all new modules |

## Total
- TASK-001 tests: 39
- TASK-002 tests: 43
- TASK-003 tests: 78
- **Total suite: 160 tests, 0 failures**
