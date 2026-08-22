# Critique 1 — TASK-094

- Spec cần làm rõ `Diagnose` fail-closed: thiếu evidence hoặc thiếu causal trace →
  escalate, không kết luận root cause (tránh đoán).
- Cần đảm bảo mọi `diagnose()` đều ghi Evidence (T001 Rule 5) qua `EvidenceStore`.
- Tích hợp Stuck (T061) qua `StuckDetector.observe/detect` để phát hiện anomaly.
- Đề xuất test deterministic: cùng incident + cùng evidence → cùng diagnosis.
- Kết luận: spec đủ, implementation cover đủ AC.
