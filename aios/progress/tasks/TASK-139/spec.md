# TASK-139 — Test Runner

## Objective
Triển khai **Test Runner** (M20) như một năng lực có contract, evidence và harness riêng — chạy test suite trong sandbox (T136) + workspace (T137) dưới policy (T138), sinh result có provenance. TASK-139 là **test runner, không phải contract mới** (dựa trên Execution Contract T135 + Sandbox T136 + Workspace T137 + Policy T138 + Evidence T001).

## Scope
**In scope:** `aios/execution/test_runner.py` — `TestRunner`, `TestRun`, `TestResult`, `TestVerdict`.
**Out of scope:** contract mới (T135), build/lint runner (T140).

## Deliverables
- `aios/execution/test_runner.py` implementation + sandbox/workspace/policy integration.
- Unit + Contract + Integration + Architecture + Regression tests (`test_test_runner.py`).
- Tích hợp: T136/T137/T138 -> T139 -> T141.

## Acceptance Criteria
- Test Runner chạy test suite trong sandbox (T136) + workspace (T137).
- Vi phạm policy (T138) -> BLOCK (fail-closed, T078).
- Mọi result có `content_hash` (T078) + provenance (T001 Rule 5).
- Test không chạy ngoài sandbox (T136/T040).
- Cùng suite + env -> cùng result (deterministic).
- Tích hợp được với Execution + Sandbox + Workspace + Policy + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T136 (Sandbox) + T137 (Workspace) + T138 (Policy) -> T139 -> T141.
- T001 (Rule 5), T078 (Integrity), T135 (Contract).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
