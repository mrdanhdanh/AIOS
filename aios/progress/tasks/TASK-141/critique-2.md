# TASK-141 — Critique 2

## Refinement
- Đồng ý Critique 1: `redact` áp dụng trước khi tính `content_hash`.
- Thêm test: capture empty -> reject (fail-closed, T078).
- `provenance()` phải bao gồm `content_hash`.

## Verdict
APPROVED — sẵn sàng BREAKDOWN.
