# Critique 1 — TASK-088

- Spec thiếu rõ contract `CompatDoc` có `rationale` + `references` → bổ sung.
- Cần làm rõ "ADR thiếu rationale → bị chặn": `review()` check `missing_rationale`.
- "Doc stale vs impl" → PUBLISHED nhưng thiếu evidence_ref → stale.
- Đề xuất test deterministic (cùng content → cùng review hash).
- Kết luận: spec đủ, implementation cover đủ AC.
