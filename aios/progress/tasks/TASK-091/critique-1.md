# Critique 1 — TASK-091

- Spec cần làm rõ mỗi `MetaCheck` có `kind` (known_answer | mutation) để `evaluate`
  đánh giá đúng theo loại — known-answer check không được ép `mutation_detected`.
- Cần đảm bảo verifier được khóa per-run qua `IntegrityChecker.lock_verifier` (T078)
  và `verifier_changed` trả False (locked).
- Tích hợp T090: `require_readiness` chỉ cho chạy meta khi coverage READY.
- Đề xuất test: known-answer đúng → PASS; harness sai → FAIL (fail-closed).
- Kết luận: spec đủ, implementation cover đủ AC.
