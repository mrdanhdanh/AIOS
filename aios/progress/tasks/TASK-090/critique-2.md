# Critique 2 — TASK-090

- `provenance_complete` dựa trên `evidence_ref` (T001 Rule 5) — mọi readiness check
  phải có provenance.
- `report_hash` phải loại trừ yếu tố không deterministic (dùng sorted gaps + round
  ratio) để cùng input → cùng hash.
- Cần test rõ: coverage thấp → NOT_READY (fail-closed) và gap được report đầy đủ.
- Kết luận: implementation đủ, sẵn sàng IMPLEMENT.
