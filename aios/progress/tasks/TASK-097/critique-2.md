# Critique 2 — TASK-097

- Confirm `ApplyOrchestrator.apply` trả về `applied=False` khi thiếu permission hoặc
  high-risk thiếu approval (fail-closed).
- `re_test_passed=False` → `rolled_back=True`, `certified=False`.
- `result_hash` dùng sha256 của JSON sort_keys → deterministic.
- Integration import-level với Permission/Governor/Harness/Certification/Simulation,
  không rewrite dependency.
- Kết luận: implementation đủ điều kiện qua review.
