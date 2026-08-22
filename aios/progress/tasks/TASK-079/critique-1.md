# Critique 1 — TASK-079

- Cần làm rõ "recorded_inputs_hash" tính từ gì: normalized inputs (JSON sort_keys) → deterministic.
- Replay phải không mutate production: Replayer chỉ đọc record, gọi evaluator trên bản
  normalized (không side-effect) → an toàn.
- Mismatch → flag non-determinism, không auto-promote → đã cover.
- Đề xuất test deterministic (cùng input → cùng hash/verdict).
- Kết luận: spec đủ.
