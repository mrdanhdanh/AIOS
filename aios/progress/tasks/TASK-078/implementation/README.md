# Implementation — TASK-078

Module: `aios/verification_integrity/`
- `integrity.py` — `IntegrityReport`, `VerifierLock`, `IntegrityChecker`.
- `tests/test_integrity.py` — 8 tests (Test Matrix).

Tích hợp: import `aios.harness.verification` / `aios.harness.evaluation` (Verdict enums)
và `aios.governance.evidence` (provenance) — không rewrite harness.
