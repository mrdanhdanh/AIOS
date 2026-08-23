# TASK-132 — Autonomy Level + Permission Integration

## Objective
Triển khai **Autonomy Level + Permission Integration** (M19) như một năng lực có contract, evidence và harness riêng — map autonomy level → tập coder operations được phép, tích hợp với permission boundary (T113). Mọi operation được check trước khi thực thi (fail-closed: denied → không silent-allow). Provenance trên mọi quyết định (T001 Rule 5).

## Scope
**In scope:** `aios/coder/autonomy.py` — `AutonomyLevel`, `AutonomyPermissionBroker`, `PermissionDecision`, `PermissionError_`.
**Out of scope:** prompt architecture (T133); file safety (T134).

## Deliverables
- `aios/coder/autonomy.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_autonomy.py`.
- Tích hợp: T125→T131 -> T132 (M19).

## Acceptance Criteria
- AC của task PASS; UNKNOWN không được nâng thành PASS (fail-closed, T078).
- Evidence có provenance (T001 Rule 5).
- Regression của dependency PASS; không vi phạm invariants.

## Dependencies
- T125..T131 -> T132.
- T001 (Rule 1/5), T113 (Security/Permission).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
