# TASK-109 — Model Contracts

## Objective
Triển khai **Model Contracts** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/contracts.py` — `ModelContract, ModelRequest, ModelResponse, UsageSchema, CapabilityDeclaration, PolicyBoundary, validate_contract`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/contracts.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T108 -> T109 -> T110/T111.

## Acceptance Criteria
- Model Contract định nghĩa rõ request/response/capabilities/usage schema.
- Contract không khóa vendor; adapter (T110) thay thế được.
- Contract không hợp lệ -> reject (fail-closed, T078).
- Mọi call có provenance (T001 Rule 5).
- Cùng input -> cùng validation (deterministic).
- Tích hợp được với Provider Registry + Model Router + Evidence.

## Dependencies
- T108 -> T109 -> T110/T111.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
