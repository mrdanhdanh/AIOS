# TASK-112 — Inference Runtime Orchestration

## Objective
Triển khai **Inference Runtime Orchestration** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/orchestration.py` — `InferenceOrchestrator, InferencePlan, ExecutionStatus`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/orchestration.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T110/T111 -> T112 -> T113/T114/T115.

## Acceptance Criteria
- Inference được orchestrate qua provider (T110) + model (T111) deterministic.
- Plan inference rule-based, không LLM (T001 Rule 4).
- Chỉ dispatch provider registered/enabled (T110).
- Provider/model không hợp lệ -> reject (fail-closed, T078).
- Mọi inference có provenance (T001 Rule 5).
- Cùng plan + state -> cùng result (deterministic).

## Dependencies
- T110/T111 -> T112 -> T113/T114/T115.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
