# Implementation — TASK-084

Module: `aios/versioning/`
- `versioning.py` — `VersionPolicy`, `ChangeType`, `VersionBump`, `VersionChange`,
  `VersionDecision`, `VersionBaseline`, `CompatibilityMatrix`, `VersionPolicyEngine`.
- `tests/test_versioning.py` — 9 tests (Test Matrix).

Tích hợp: import `aios.contracts.contract` (T064, `DEFAULT_DEPRECATION_WINDOW`)
và reference `aios.migration` (T074) / `aios.upgrade` (T074) — không rewrite.
