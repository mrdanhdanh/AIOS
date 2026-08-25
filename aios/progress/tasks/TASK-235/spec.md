# TASK-235 — Evidence Quality & Integrity

> **Trạng thái:** PLANNED (2026-08-25) — phase AIOS 2.x / M32.
> Chi tiết đầy đủ: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

## Mục tiêu
Conflict detection, replay, quality score; evaluation CHỈ dựa trên evidence hợp lệ (non-UNKNOWN, non-STALE).

## Phạm vi
- `EvidenceStore`: detect conflict, replay (tái tạo từ Run), quality score (producer trust × freshness × verification).
- `Evaluation` từ chối evidence `UNKNOWN`/`STALE`/conflict.

## Deliverables
- `aios/governance/evidence/` (conflict/replay/quality) + `aios/evaluation/` (valid-evidence gate) + test + artifacts.

## Acceptance Criteria
- Conflict detection báo cáo đúng cặp mâu thuẫn.
- Replay tái tạo Evidence từ Run gốc.
- Quality score tính đúng; evaluation bỏ qua UNKNOWN/STALE/conflict.
- Architecture gate 0 violations; full suite không regress.

## Dependencies / Gate
TASK-234, TASK-030, TASK-032, TASK-001. Milestone M32.
