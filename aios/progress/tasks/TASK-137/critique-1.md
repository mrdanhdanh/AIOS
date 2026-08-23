# TASK-137 — Critique 1

## Missing / risky sections
- Cần enforce `workspace_id`/`snapshot_id` immutable (T001 Rule 1).
- `snapshot` phải sinh `state_hash` (T078) và reject state rỗng (fail-closed).
- `restore` phải trả về `state_hash` để rollback (T020/T066).

## Risks
- Nếu snapshot không hash được mà vẫn lưu -> mất integrity (T078).
- Thiếu provenance -> không trace được checkpoint.

## Verdict
SPEC acceptable; cần fail-closed snapshot + immutable id.
