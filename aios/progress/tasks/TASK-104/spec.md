# TASK-104 — Independent Harness Integration Foundation

## Objective
Xây **nền tảng tích hợp Independent Harness** vào AIOS — định nghĩa adapter contract, registration (`harness_id` immutable, T001 Rule 1), evidence ingest boundary (fail-closed, provenance T078/T001), và giữ **authority/policy ở AIOS**. Đây là foundation của M16, không phải harness mới (dựa trên Harness T030/T032 + Integrity T078 + Evidence T001).

## Scope
**In scope:** `aios/independent_harness/foundation.py` — `IndependentHarnessAdapter`, `HarnessRegistry`, `EvidenceIngestBoundary`, `PolicyAuthority` + tests. Tích hợp Harness (T030/T032) + Integrity (T078) + Evidence (T001).
**Out of scope:** harness mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/independent_harness/foundation.py` — adapter/registry/ingest/policy (6 tests).
- `aios/independent_harness/tests/test_independent_harness.py` — Test Matrix T104.
- Tích hợp Harness (T030/T032) + Integrity (T078) + Evidence (T001) + Oracle (T105).

## Acceptance Criteria
- Adapter Contract định nghĩa rõ (interface + schema).
- Registration hoạt động; `harness_id` immutable (T001 Rule 1).
- Evidence Ingest Boundary enforce (thiếu provenance → reject, T078).
- AIOS giữ authority/policy; independent harness không ghi đè verdict.
- Mọi ingest có provenance (T001 Rule 5).
- Cùng adapter + input → cùng kết quả (deterministic).
- Tích hợp được với Harness + Integrity + Evidence + Oracle (T105).
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T103 (Autonomy Constitution) → T104 → T105.
- T030/T032 (Harness), T078 (Integrity), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. `independent_harness` là `unknown` layer; chỉ import stdlib + `aios.harness` + `aios.verification_integrity` + `aios.governance.evidence`.
