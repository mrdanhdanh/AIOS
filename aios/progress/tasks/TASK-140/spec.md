# TASK-140 — Build / Lint Runner

## Objective
Triển khai **Build / Lint Runner** (M20) như một năng lực có contract, evidence và harness riêng — chạy build/lint trong sandbox (T136) + workspace (T137) dưới policy (T138), sinh result có provenance. TASK-140 là **build/lint runner, không phải contract mới** (dựa trên Execution Contract T135 + Sandbox T136 + Workspace T137 + Policy T138 + Evidence T001).

## Scope
**In scope:** `aios/execution/build_lint.py` — `BuildLintRunner`, `BuildLintRun`, `BuildResult`, `LintResult`, `BuildVerdict`, `LintVerdict`.
**Out of scope:** contract mới (T135), test runner (T139).

## Deliverables
- `aios/execution/build_lint.py` implementation + sandbox/workspace/policy integration.
- Unit + Contract + Integration + Architecture + Regression tests (`test_build_lint.py`).
- Tích hợp: T136/T137/T138 -> T140 -> T141.

## Acceptance Criteria
- Build/Lint Runner chạy build/lint trong sandbox (T136) + workspace (T137).
- Vi phạm policy (T138) -> BLOCK (fail-closed, T078).
- Mọi result có `content_hash` (T078) + provenance (T001 Rule 5).
- Build/Lint không chạy ngoài sandbox (T136/T040).
- Cùng target + env -> cùng result (deterministic).
- Tích hợp được với Execution + Sandbox + Workspace + Policy + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T136 (Sandbox) + T137 (Workspace) + T138 (Policy) -> T140 -> T141.
- T001 (Rule 5), T078 (Integrity), T135 (Contract).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
