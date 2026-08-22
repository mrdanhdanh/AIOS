# Critique 2 — TASK-093

- `review_hash` deterministic: cùng result → cùng hash (dùng sorted notes).
- `provenance_complete` dựa trên `evidence_ref` của doc (T001 Rule 5).
- Doc thực tế (`docs/behavioral_spec.md`, `docs/adr/ADR-0008.md`) phải khớp implementation
  DONE (không stale) — reviewer kiểm tra tồn tại file reference.
- Cần test rõ: cùng content → cùng review (deterministic); link valid → không 404.
- Kết luận: implementation đủ, sẵn sàng IMPLEMENT.
