# TASK-237 — Unified Control Center Dashboard

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M34.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Dashboard trở thành Control Center với views: Goals, Executions, Agents, Plans, Coding, Evidence, Verification, Autonomy, Resources, Policies, Artifacts, Failures, Recovery, System Health. Mọi data qua API; không logic riêng ở frontend.

## Phạm vi
- Mở rộng `aios/dashboard/` + `aios/api/` routers expose state thật.
- Frontend chỉ render; mọi compute nằm backend.
- Tận dụng `observability` (T021) + `operations` (T042).

## Deliverables
- `aios/dashboard/` (Control Center views) + `aios/api/` (state routers) + test + artifacts.

## Acceptance Criteria
- Dashboard hiển thị đủ 14 views từ API state thật.
- 0 business logic ở frontend.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-229, TASK-234, TASK-236, TASK-017, TASK-018, TASK-001. Milestone M34.
