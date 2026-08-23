# TASK-113 — Credential + Permission + Policy Integration

## Objective
Triển khai **Credential + Permission + Policy Integration** (M17) như một năng lực có contract, evidence và harness riêng, tích hợp với các task phụ thuộc theo dependency của milestone.

## Scope
**In scope:** `aios/model_runtime/security.py` — `SecurityGate, SecurityContext, CredentialBoundary, PermissionCheck, PolicyPrecheck`.
**Out of scope:** provider/filesystem adapters mới; vendor lock-in.

## Deliverables
- `aios/model_runtime/security.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Tích hợp theo dependency: T112 -> T113 -> T114/T115.

## Acceptance Criteria
- Mọi inference (T112) qua permission + policy trước execution.
- Credential value không lộ trong evidence/log (T040).
- Thiếu permission/policy -> BLOCK (fail-closed, T078).
- Mọi decision có provenance (T001 Rule 5), không chứa secret.
- Cùng context + policy -> cùng decision (deterministic).
- Tích hợp được với Inference + Identity + Sandbox + Quota + Evidence.

## Dependencies
- T112 -> T113 -> T114/T115.
- T001 (Evidence/Rule 5), T078 (Integrity), T025 (Health), T040 (Credential), T049 (Certification) theo từng task.

## Governance references
- Rule 1..7 via `aios/governance/*`. `model_runtime` là `unknown` (infra) layer.
