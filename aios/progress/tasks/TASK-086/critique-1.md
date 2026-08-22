# Critique 1 — TASK-086

- Spec thiếu rõ contract `CompatResult` có `blocked` flag → bổ sung.
- Cần làm rõ "break 1.0 consumer → BLOCK": `check()` trả blocked=True khi breaking.
- Compat test suite phải lock 1.0 behavior → `CompatTestSuite` wrapper.
- Đề xuất test deterministic (cùng surface + version → cùng result).
- Kết luận: spec đủ, implementation cover đủ AC.
