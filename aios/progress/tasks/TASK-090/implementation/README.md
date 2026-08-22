# TASK-090 Implementation

Harness Coverage + Readiness implementation lives in `aios/harness_coverage/`:

- `aios/harness_coverage/coverage.py` — `CoverageMap`, `CoverageChecker`,
  `CoverageReport`, `Readiness`.
- `aios/harness_coverage/tests/test_coverage.py` — 7 coverage/readiness tests.

Integration (import-level, no rewrite):
- `aios.certification.certifier` (Certifier, Certification, CertStatus) — T073
- `aios.behavioral.behavioral` (BehaviorScenario) — T089
