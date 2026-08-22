# Implementation — TASK-086

Module: `aios/backward_compat/`
- `backward.py` — `CompatSurface`, `CompatCheck`, `CompatResult`,
  `CompatSuiteResult`, `BackwardCompatChecker`, `CompatTestSuite`.
- `tests/test_backward.py` — 7 tests (Test Matrix).

Tích hợp: import `aios.contracts.contract` (T064, `ContractSurface`),
`aios.versioning.versioning` (T084, `CompatibilityMatrix`) — không rewrite.
