# TASK-230 — Coder Agent ↔ Capability Registry

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M30.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Nối `CoderAgent` (M19–M26 Coding Plane) với `Capability Registry` (`aios/capability/`) qua interface injected thay vì gọi trực tiếp. Tuân ARCH-001..004.

## Phạm vi
- `aios/coder/` nhận `CapabilityRegistry` (injected), resolve tool/capability theo tên.
- `CoderAgent` pure / I/O-free, capability-injected (pattern `SelfImproverAgent` T225).
- Test: resolve capability, fail-closed khi capability không tồn tại.

## Deliverables
- `aios/coder/` (wiring) + test + task artifacts + evidence.

## Acceptance Criteria
- Coder resolve capability qua registry (không direct import).
- Thiếu capability → fail-closed (không guess).
- 0 vi phạm ARCH-001..004; full suite không regress.

## Dependencies / Gate
TASK-218, TASK-009, TASK-001. Milestone M30.
