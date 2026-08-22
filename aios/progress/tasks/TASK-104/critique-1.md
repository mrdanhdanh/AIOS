# Critique 1 — TASK-104

- **Thiếu định nghĩa rõ schema evidence_format:** cần chuẩn hóa `evidence_format` thành versioned string ("aios-evidence-v1") để ingest boundary parse được. → Đã thêm `evidence_format` mặc định trong `IndependentHarnessAdapter`.
- **Chưa nói rõ idempotency của ingest:** cùng evidence_id ingest 2 lần phải ra cùng kết quả (deterministic). → Đã thêm kiểm tra `_evidence_is_present` trả về accepted=True (idempotent).
- **Authority boundary chưa explicit:** cần hàm `reject_override` để chặn independent harness ghi đè verdict AIOS. → Đã thêm `PolicyAuthority.reject_override`.
- **Thiếu test fail-closed tamper:** cần test hash mismatch bị reject. → Đã có trong Test Matrix (ingest missing hash). Bổ sung thêm tamper test trong implementation.
