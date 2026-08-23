# TASK-134 — File Safety Boundary + Scope Enforcement

## Objective
Triển khai **File Safety Boundary + Scope Enforcement** (M19) như một năng lực có contract, evidence và harness riêng — enforce coder file operations chỉ trong allowed scope root. Mọi path escape (traversal, absolute outside, symlink escape) bị reject fail-closed. Đây là safety boundary ngăn coder chạm file ngoài workspace được authorize (T113 spirit / security). Provenance trên mọi quyết định (T001 Rule 5).

## Scope
**In scope:** `aios/coder/filesafety.py` — `FileSafetyBoundary`, `ScopeDecision`, `ScopeStatus`, `FileSafetyError`.
**Out of scope:** M20 (Execution Contract T135...).

## Deliverables
- `aios/coder/filesafety.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_filesafety.py`.
- Tích hợp: T125→T133 -> T134 (đóng M19).

## Acceptance Criteria
- AC của task PASS; UNKNOWN không được nâng thành PASS (fail-closed, T078).
- Evidence có provenance (T001 Rule 5).
- Regression của dependency PASS; không vi phạm invariants.

## Dependencies
- T125..T133 -> T134 (đóng M19).
- T001 (Rule 5), T113 (Security).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
