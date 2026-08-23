# Critique 1 — TASK-128

## Missing / weak sections
- Spec cần làm rõ backup-before-apply (T020) và rollback-to-certified (T020/T066) là bắt buộc fail-closed.
- Cần quy định diff deterministic (cùng artifact + target → cùng diff).

## Risks
- Nếu apply fail mà không rollback → repo hỏng (vi phạm T020/T066).
- Nếu không backup → không thể rollback.

## Recommendations
- `PatchEngine.apply()` luôn backup trước; exception → rollback + `PatchError`.
- Mọi `PatchRun` ghi `content_hash` (sha256) + `evidence_id` (T001 Rule 5).
- Test cover fail-closed rollback + architecture (no forbidden imports).
