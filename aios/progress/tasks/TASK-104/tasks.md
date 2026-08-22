# Breakdown — TASK-104

1. `IndependentHarnessAdapter` dataclass (frozen) — contract với `harness_id` immutable, `policy_authority="aios"`.
2. `HarnessRegistry.register/get/list` — reject duplicate `harness_id` (T001 Rule 1).
3. `EvidencePayload` + `EvidenceIngestBoundary.ingest` — fail-closed provenance + tamper check, idempotent.
4. `PolicyAuthority` — `reject_override`, `authoritative_verdict`, `is_aios_authoritative`.
5. Tests (6) theo Test Matrix T104.
6. Tích hợp import-level với Harness (T030/T032) + Integrity (T078) + Evidence (T001).
