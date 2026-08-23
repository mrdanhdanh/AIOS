# TASK-145 — Coding Loop State Machine

## Objective
Triển khai **Coding Loop State Machine** (M21) như một năng lực có contract, evidence và harness riêng — điều khiển vòng lặp coding tự chủ (observe → classify → diagnose → repair → verify → refresh → safety) qua một state machine xác định, fail-closed. TASK-145 là **state machine điều khiển, không phải execution mới** (dựa trên Autonomous Loop T053 + Goal Engine T050 + Evidence T001 + Lifecycle T001 Rule 6).

## Scope
**In scope:** `aios/coding_loop/state_machine.py` — `CodingLoopStateMachine`, `CodingLoopState`, `CodingLoopRecord`, `TransitionEvent`, `TRANSITIONS`.
**Out of scope:** execution mới (T135–T144).

## Deliverables
- `aios/coding_loop/state_machine.py` implementation + state machine.
- Policy Boundary (T113) trên mọi transition.
- Integration với Autonomous Loop (T053) + Goal Engine (T050) + Evidence (T001) + Lifecycle (T001 Rule 6).
- Unit + Contract + Integration + Architecture + Regression tests (`test_state_machine.py`).

## Acceptance Criteria
- Coding Loop State Machine định nghĩa states + transitions xác định.
- Mọi transition có điều kiện artifact bắt buộc (T001 Rule 6).
- Thiếu artifact → reject transition (fail-closed).
- `loop_id` immutable (T001 Rule 1).
- Cùng state + input → cùng next state (deterministic).
- Tích hợp được với Autonomous Loop + Goal Engine + Evidence + Lifecycle.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T144 (Execution Evidence), T053 (Autonomous Loop), T050 (Goal Engine).
- T001 (Rule 1/5/6), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
