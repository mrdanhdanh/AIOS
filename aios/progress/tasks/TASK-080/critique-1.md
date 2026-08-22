# Critique 1 — TASK-080

- Cần làm rõ "UI state" capture: dùng bytes (screenshot) hoặc str (DOM) → capture() nhận
  bytes|str, normalize sang str để hash → deterministic.
- Baseline approval phải require evidence_ref → đã enforce (VisualError nếu thiếu).
- Visual regression diff: dùng Hamming distance trên hex hash → score [0,1], threshold mặc định 0.05.
- Đề xuất test deterministic (cùng state+config → cùng hash).
- Kết luận: spec đủ.
