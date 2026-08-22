# TASK-105 Implementation

Independent Verification Oracle lives in `aios/independent_harness/`:

- `aios/independent_harness/oracle.py` — `OracleResult`, `InvariantMapping`, `IndependentVerificationOracle`.
- Tests trong `aios/independent_harness/tests/test_independent_harness.py` (Test Matrix T105).

Integration (import-level, no rewrite):
- `aios.independent_harness.foundation` (HarnessRegistry, EvidenceIngestBoundary, PolicyAuthority) — T104
- `aios.verification_integrity` (VerdictClass, IntegrityChecker) — T078
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
