# Critique 1 — TASK-098

- Spec cần làm rõ `RemediationIntegrityGate.check` fail-closed: artifact bị sửa
  (hash không khớp T078) → reject; thiếu audit trail → reject.
- Cần đảm bảo remediation đang chạy tôn trọng Kill Switch (T068) qua
  `hook_kill_switch` + `should_halt`.
- Tích hợp Integrity (T078) qua `IntegrityChecker.is_tampered/sha256` để detect tamper.
- Đề xuất test deterministic: cùng artifact + cùng check → cùng result.
- Kết luận: spec đủ, implementation cover đủ AC.
