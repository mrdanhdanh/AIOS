# TASK-115 — Usage / Cost / Audit / Evidence

## Objective
Triển khai **Usage / Cost / Audit / Evidence** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/usage.py` — `UsageCollector, UsageRecord, AuditLog, CostCompute, AuditEntry`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/usage.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T112/T114 -> T115 -> T116.

## Acceptance Criteria
- Mọi inference call sinh UsageRecord + AuditEntry.
- AuditEntry bất biến, tamper-evident (T078).
- UsageRecord có content_hash (T078) + provenance (T001 Rule 5).
- Cost tính theo quota/budget (T039).
- Usage thiếu hash/provenance -> reject (fail-closed, T078).
- Cùng call -> cùng usage/cost (deterministic).

## Dependencies
- T112/T114 -> T115 -> T116.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
