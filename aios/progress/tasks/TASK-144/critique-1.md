# TASK-144 — Critique 1

## Missing / risky sections
- `evidence_id` immutable + không tái sử dụng (T001 Rule 1).
- `promote` phải reject khi `integrity_verified=False` (fail-closed, T078).
- `evidence_chain` phải ghi đầy đủ provenance (T001 Rule 5).

## Risks
- Nếu evidence chưa verify mà promote PASS -> vi phạm T078.
- Nếu chain thiếu -> không trace được nguồn.

## Verdict
SPEC acceptable; cần fail-closed promote + immutable id.
