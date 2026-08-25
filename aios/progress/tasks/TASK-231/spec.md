# TASK-231 — CodingEdition ↔ RealToolHandler

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M30.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Nối `CodingEdition.run(authorization=..., generated_code=..., verification_report=...)` (M26) với `RealToolHandler` (T222) để AIOS **thực sự viết + thực thi code** dưới Policy/Permission. Định nghĩa execution contract cho code generation.

## Phạm vi
- `CodingEdition` gọi `RealToolHandler` (shell/file/git) được Policy pre-check.
- Contract: generated_code → write → (optional) run tests → collect output → verification_report.
- Mọi file mutation qua `PermissionBroker` + `PolicyEngine` (fail-closed).
- `real_execution.enabled` vẫn opt-in (safe default).

## Deliverables
- `aios/coding_edition/` (RealToolHandler wiring) + test + task artifacts + evidence.

## Acceptance Criteria
- `CodingEdition.run(...)` thực thi code thật qua `RealToolHandler` khi `real_execution.enabled=true`.
- Mutation thiếu permission → DENY (không ghi file).
- Contract sinh `verification_report` hợp lệ.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-230, TASK-222, TASK-218, TASK-001. Milestone M30.
