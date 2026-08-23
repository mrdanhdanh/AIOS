# TASK-153 — Autonomous Safety Controller

## Objective
Triển khai **Autonomous Safety Controller** (M21) như một năng lực có contract, evidence và harness riêng — đặt boundary/an toàn cho coding tự chủ (giới hạn blast radius), dựa trên Autonomy Safety (T067) + Kill Switch (T068). TASK-153 là **safety controller, không phải loop mới** (dựa trên Context Refresh + Patch Chain T152 + Autonomy Safety T067 + Kill Switch T068 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/safety.py` — `AutonomousSafetyController`, `SafetyDecision`.
**Out of scope:** loop mới (T145).

## Deliverables
- `aios/coding_loop/safety.py` implementation + safety controller.
- Policy Boundary (T113) trên mọi decision.
- Integration với Context Refresh + Patch Chain (T152) + Autonomy Safety (T067) + Kill Switch (T068) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_safety.py`).

## Acceptance Criteria
- Safety Controller giới hạn blast radius của loop.
- Vi phạm boundary → kill switch kích hoạt (T068).
- Mọi decision có provenance (T001 Rule 5).
- Cùng state → cùng decision (deterministic).
- Guardrail từ T067 được áp dụng.
- Tích hợp được với Context Refresh + Patch Chain + Autonomy Safety + Kill Switch + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T152 (Context Refresh + Patch Chain), T067 (Autonomy Safety 1.0), T068 (Kill Switch).
- T001 (Rule 5), T067 (Safety), T068 (Kill Switch), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
