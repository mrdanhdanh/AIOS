# TASK-104 Implementation

Independent Harness Integration Foundation lives in `aios/independent_harness/`:

- `aios/independent_harness/foundation.py` — `IndependentHarnessAdapter`, `HarnessRegistry`, `EvidenceIngestBoundary`, `PolicyAuthority`, `EvidencePayload`, `IngestResult`.
- `aios/independent_harness/tests/test_independent_harness.py` — Test Matrix T104 (6 tests).

Integration (import-level, no rewrite):
- `aios.harness.contracts` (HarnessSpec, RunResult, Assertion) — T030/T032
- `aios.verification_integrity` (IntegrityChecker, VerdictClass, sha256) — T078
- `aios.governance.evidence.store` (EvidenceStore, Evidence) — T001 Rule 5
