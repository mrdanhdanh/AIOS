# Critique 2 — TASK-085

- Verifier: `apply()` fail-closed đúng (verify FAIL → FAILED, no mutation).
- `rollback()` chạy `down` ngược thứ tự → về 1.0.
- `plan_hash` deterministic cho provenance.
- Tích hợp T074/T032/T084 import-level, không rewrite.
- Không vi phạm architecture (unknown layer).
- Kết luận: APPROVED.
