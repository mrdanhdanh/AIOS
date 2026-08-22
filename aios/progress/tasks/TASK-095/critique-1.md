# Critique 1 — TASK-095

- Spec cần làm rõ `PolicyFilter` fail-closed: candidate vi phạm policy (T054/T067)
  → bị loại khỏi ranked plan, không apply.
- Cần đảm bảo `risk_score` evidence-based (impact, rollback_cost, blast_radius),
  không đoán.
- Tích hợp Governor (T054) qua `AutonomyGovernor.decide(ActionContext)` để xác định
  policy_compliant.
- Đề xuất test deterministic: cùng diagnosis + cùng policy → cùng ranking.
- Kết luận: spec đủ, implementation cover đủ AC.
