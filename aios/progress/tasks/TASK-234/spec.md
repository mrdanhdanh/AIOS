# TASK-234 — Automatic Evidence Generation

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M32.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Mọi execution tự động sinh Evidence với provenance; tracking coverage theo requirement và freshness.

## Phạm vi
- Hook trong `RuntimeKernel.execute_plan` (T229) tự emit Evidence mỗi Run.
- `EvidenceStore` thêm `requirement_id`, `freshness` (TTL), `coverage` map.
- Test: coverage theo requirement, freshness expiry.

## Deliverables
- `aios/runtime/` (evidence hook) + `aios/governance/evidence/` (coverage/freshness) + test + artifacts.

## Acceptance Criteria
- Mọi execution sinh Evidence tự động.
- Evidence có `requirement_id` + `freshness`; expired → STALE.
- Coverage map requirement→evidence đầy đủ.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-229, TASK-005, TASK-001. Milestone M32.
