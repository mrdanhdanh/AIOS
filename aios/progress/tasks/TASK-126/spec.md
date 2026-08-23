# TASK-126 — Coding Planner + PlanVerifier

## Objective
Triển khai **Coding Planner + PlanVerifier** (M19) như một năng lực có contract, evidence và harness riêng — lập kế hoạch coding (deterministic-first) và verify plan trước khi thực thi, không để LLM làm control plane. TASK-126 là **planner + verifier, không phải generator mới** (dựa trên Coder Agent T125 + Planning Engine T026 + Deterministic T001 Rule 4).

## Scope
**In scope:** `aios/coder/planner.py` — `CodingPlanner`, `PlanVerifier`, `CodingPlan`, `CodingStep`, `PlanStatus`, `PlanVerifyError`.
**Out of scope:** code generation runtime (T127); patch engine (T128).

## Deliverables
- `aios/coder/planner.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_planner.py`.
- Tích hợp: T125 -> T126 -> T127/T128 (M19).

## Acceptance Criteria
- Planner lập coding plan deterministic-first (rule trước LLM).
- Rule đủ → `llm_call_count = 0` (T001 Rule 4).
- PlanVerifier verify plan trước execution; FAIL → reject (fail-closed, T078).
- Mọi plan có provenance (T001 Rule 5).
- Cùng request + rule → cùng plan (deterministic).
- Tích hợp được với Coder Agent + Planning Engine + Deterministic + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T125 (Coder Agent) -> T126 -> T127/T128.
- T001 (Rule 4/5), T026 (Planning Engine), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
