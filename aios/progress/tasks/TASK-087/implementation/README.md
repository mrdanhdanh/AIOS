# Implementation — TASK-087

Module: `aios/conformance/`
- `conformance.py` — `ConformanceCheck`, `ConformanceReport`, `ConformanceRunner`.
- `tests/test_conformance.py` — 7 tests (Test Matrix).

Tích hợp: import `aios.backward_compat.backward` (T086), `aios.contracts.contract`
(T064, `Contract`/`ContractStatus`), `aios.versioning.versioning` (T084,
`CompatibilityMatrix`/`VersionBaseline`), `aios.certification.certifier` (T073,
`Certifier`) — không rewrite.
