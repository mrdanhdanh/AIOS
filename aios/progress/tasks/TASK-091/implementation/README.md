# TASK-091 Implementation

Meta-Harness / Verify-the-Verifier implementation lives in `aios/meta_harness/`:

- `aios/meta_harness/meta.py` — `MetaCheck`, `MetaResult`, `MetaHarness`, `MetaVerdict`.
- `aios/meta_harness/tests/test_meta.py` — 7 meta-verification tests.

Integration (import-level, no rewrite):
- `aios.verification_integrity.integrity` (IntegrityChecker, VerifierLock) — T078
- `aios.harness_coverage.coverage` (CoverageReport, Readiness) — T090
