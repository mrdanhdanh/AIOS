# TASK-135 — Execution Contract

## Objective
Triển khai **Execution Contract** (M20) như một năng lực có contract, evidence và harness riêng — định nghĩa contract chuẩn cho thực thi (request/response, sandbox ref, policy ref, artifact ref) mà mọi execution task M20 dùng chung. TASK-135 là **foundation của M20, không phải runner mới** (dựa trên Execution T005 + Coder Pipeline T125–T130 + Evidence T001).

## Scope
**In scope:** `aios/execution/contract.py` — `ExecutionContract`, `ExecutionRequest`, `ExecutionResponse`, `ExecutionStatus`, `CapabilityDispatcher`.
**Out of scope:** sandbox/workspace/policy/runner mới (T136–T143).

## Deliverables
- `aios/execution/contract.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/execution/tests/test_contract.py`.
- Tích hợp theo dependency: T130 -> T135 -> T136/T137/T138.

## Acceptance Criteria
- Execution Contract định nghĩa rõ request/response/sandbox/policy/artifact schema.
- Contract không hợp lệ -> reject (fail-closed, T078).
- Mọi execution có provenance (T001 Rule 5).
- Cùng input -> cùng validation (deterministic).
- Tích hợp được với Execution + Coder Pipeline + Sandbox + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T130 (Coding Artifact) -> T135 -> T136/T137/T138.
- T001 (Evidence/Rule 5), T005 (Execution), T113 (Policy), T078 (Integrity).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
