# Critique 2 — TASK-092

- `certify` fail-closed: chỉ `READY_TRUSTED` mới issue+certify qua Certifier (T073);
  các trạng thái khác → None.
- `provenance_complete` dựa trên `evidence_ref` (T001 Rule 5).
- `trust_hash` deterministic: cùng inputs → cùng hash.
- Cần test rõ: not ready + trusted → không certify; cùng system+harness → cùng trust.
- Kết luận: implementation đủ, sẵn sàng IMPLEMENT.
