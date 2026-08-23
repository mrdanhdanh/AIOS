# TASK-111 — Model Registry + Deterministic Resolver

## Objective
Triển khai **Model Registry + Deterministic Resolver** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/model_registry.py` — `ModelRegistry, ModelResolver, ResolveStatus`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/model_registry.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T109 -> T111 -> T112/T116.

## Acceptance Criteria
- Model Registry hoạt động; model_id immutable (T001 Rule 1).
- Resolver chạy deterministic (rule, không LLM) - LLM call count = 0.
- Cùng request + registry/policy -> cùng selected_model (deterministic).
- Không resolve được -> reject (fail-closed, T078).
- Mọi resolve có provenance (T001 Rule 5).
- Tích hợp được với Model Contract + Provider Registry + Model Router + Evidence.

## Dependencies
- T109 -> T111 -> T112/T116.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
