# TASK-149 — Repair Planner

## Objective
Triển khai **Repair Planner** (M21) như một năng lực có contract, evidence và harness riêng — lập kế hoạch repair (patch) từ diagnostic report (T148), dùng Planning Engine (T026) + Autonomous Recovery (T055). TASK-149 là **planner, không phải executor mới** (dựa trên Diagnostic Agent T148 + Planning Engine T026 + Autonomous Recovery T055 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/repair.py` — `RepairPlanner`, `RepairPlan`.
**Out of scope:** executor mới (T127/T128).

## Deliverables
- `aios/coding_loop/repair.py` implementation + planner.
- Policy Boundary (T113) trên mọi plan.
- Integration với Diagnostic Agent (T148) + Planning Engine (T026) + Autonomous Recovery (T055) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_repair.py`).

## Acceptance Criteria
- Repair Planner sinh plan từ diagnostic report (T148).
- Mọi plan có rollback (T055).
- Mọi plan có provenance (T001 Rule 5).
- Cùng diagnosis → cùng plan (deterministic).
- Plan không vượt policy boundary (T113).
- Tích hợp được với Diagnostic Agent + Planning Engine + Autonomous Recovery + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T148 (Diagnostic Agent), T026 (Planning Engine), T055 (Autonomous Recovery).
- T001 (Rule 5), T055 (Recovery), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
