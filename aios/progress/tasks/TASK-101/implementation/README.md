# TASK-101 Implementation

Continuous Certification lives in `aios/continuous_certification/`:

- `aios/continuous_certification/cert.py` — `CertGate`, `ContinuousCertRun`, `ContinuousCertEngine`.
- `aios/continuous_certification/tests/test_cert.py` — 6 cert tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.certification.certifier` (Certifier) — T073
- `aios.conformance.conformance` (ConformanceRunner) — T087
- `aios.harness_coverage` (CoverageChecker, CoverageReport, Readiness) — T090
- `aios.meta_harness` (MetaHarness, MetaResult, MetaVerdict) — T091
- `aios.readiness_trust.trust` (TrustGate, CombinedTrust) — T092
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
