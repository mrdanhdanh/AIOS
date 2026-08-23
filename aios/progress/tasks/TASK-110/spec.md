# TASK-110 — Provider Registry + Lifecycle

## Objective
Triển khai **Provider Registry + Lifecycle** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/provider_registry.py` — `ProviderRegistry, ProviderRecord, LifecycleEvent, ProviderStatus, HealthStatus`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/provider_registry.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T109 -> T110 -> T112/T116.

## Acceptance Criteria
- Provider Registry hoạt động; provider_id immutable (T001 Rule 1).
- Lifecycle register/enable/disable/deprecate đầy đủ.
- Provider unhealthy -> không được chọn (T025).
- Provider không hợp lệ -> reject (fail-closed, T078).
- Mọi lifecycle event có provenance (T001 Rule 5).
- Provider thay thế được qua contract (T109), không vendor lock.

## Dependencies
- T109 -> T110 -> T112/T116.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
