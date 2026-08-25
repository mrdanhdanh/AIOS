# TASK-232 — Automated Test / Static Analysis + Code Provenance

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M30.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Sau khi sinh code, AIOS tự động chạy test + static analysis; artifact code mang provenance đầy đủ; mọi mutation qua Policy. Đóng vòng "viết code có chứng cứ".

## Phạm vi
- Hook post-generation: chạy test/static-analysis qua `RealToolHandler` (policy-checked).
- Mỗi artifact code sinh `Evidence` (content_hash, producer, source, parent_artifact).
- Báo cáo tổng hợp (pass/fail/coverage) đẩy vào `Evaluation`.

## Deliverables
- `aios/coding_edition/` (post-gen hook) + test + task artifacts + evidence.

## Acceptance Criteria
- Sinh code → auto chạy test/static-analysis → kết quả vào Evidence.
- Code artifact có provenance chain complete.
- Thiếu permission → không chạy (fail-closed).
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-231, TASK-005, TASK-001. Milestone M30.
