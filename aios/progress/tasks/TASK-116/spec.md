# TASK-116 — Provider Conformance + Certification

## Objective
Triển khai **Provider Conformance + Certification** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/conformance.py` — `ConformanceSuite, ProviderCertifier, ProviderCertification, ConformanceResult`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/conformance.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T110/T111/T112/T115 -> T116 -> T117 (M18).

## Acceptance Criteria
- Conformance Suite chạy check provider (T110) + model (T111) theo contract (T109).
- Conformance FAIL/INCONCLUSIVE -> không certify (fail-closed, T078).
- Certification chỉ cấp khi PASS + integrity verified (T078).
- cert_id immutable (T001 Rule 1, T049).
- Mọi conformance run có provenance (T001 Rule 5).
- Cùng provider/model + suite -> cùng result (deterministic).

## Dependencies
- T110/T111/T112/T115 -> T116 -> T117 (M18).
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
