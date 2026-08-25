# TASK-233 — Unified Autonomous Lifecycle

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M31.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Hợp nhất `autonomous_loop`, `autonomous_recovery`, `evaluation`, `autonomous_experimentation`, `stuck_detection`, `autonomy_governor`, `coding_loop` thành MỘT lifecycle duy nhất. Không tạo subsystem mới.

## Phạm vi
- `Goal → Plan → Execute → Observe → Evaluate → [Success→DONE | Fail→Diagnose→Repair→Simulate→Policy→Apply→Verify→loop]`.
- Các module đã có map vào node; `RetryGuard` (T226) + `KillSwitch` (M10) là guard.

## Deliverables
- `aios/autonomous_loop/lifecycle.py` (Unified Autonomous Lifecycle) + test + artifacts + evidence.

## Acceptance Criteria
- Loop chạy end-to-end trên scenario giả lập: Plan→Execute→Observe→Evaluate→(fail)→Diagnose→Repair→Simulate→Apply→Verify→loop→DONE.
- Mọi transition qua Policy/Permission (fail-closed).
- KillSwitch / RetryGuard kích hoạt đúng điều kiện.
- 0 vi phạm ARCH-001..004; full suite không regress.

## Dependencies / Gate
TASK-229, TASK-232, TASK-226, TASK-041, TASK-001. Milestone M31.
