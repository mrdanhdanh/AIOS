# Critique 1 — TASK-089

- Spec cần làm rõ `BehaviorScenario.is_observable()` — chỉ scenario có given/when/then
  và `observable=True` mới hợp lệ; ngược lại → bị chặn (fail-closed).
- Cần đảm bảo mọi `observe()` đều ghi Evidence (T001 Rule 5) qua `EvidenceStore`.
- Tích hợp Harness (T030) qua `VerificationPipeline` (precondition observable,
  postcondition conforms) và `ReplayEngine` (determinism check).
- Đề xuất test deterministic: cùng scenario + cùng driver → cùng observable.
- Kết luận: spec đủ, implementation cover đủ AC.
