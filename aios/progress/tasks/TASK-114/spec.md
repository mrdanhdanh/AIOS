# TASK-114 — Retry / Timeout / Streaming / Cancellation

## Objective
Triển khai **Retry / Timeout / Streaming / Cancellation** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/resilience.py` — `ResilienceManager, ResilienceConfig, CancellationToken, StreamChunk, ResilienceStatus`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/resilience.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T112/T113 -> T114 -> T115.

## Acceptance Criteria
- Retry bounded, không loop vô hạn (T005).
- Timeout hết -> fail-closed, không treo (T078).
- Streaming chunk có provenance (T001 Rule 5).
- Cancellation giải phóng resource (T005).
- Retry/timeout vượt -> reject (fail-closed, T078).
- Cùng config + failure -> cùng behavior (deterministic).

## Dependencies
- T112/T113 -> T114 -> T115.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
