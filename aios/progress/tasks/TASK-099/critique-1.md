# Critique 1 — TASK-099

- Spec cần làm rõ loop fail-closed: deviation → không promote PASS, trigger detect (T094).
- Remediation chỉ trigger khi Governor allow (T054/T067) — autonomy-gated, không auto-apply.
- Mọi loop run phải ghi Evidence (T001 Rule 5) qua EvidenceStore.
- Tích hợp Scheduler (T062) qua `trigger_due` để xác định đến hạn.
- Đề xuất test deterministic: cùng system state + cùng harness → cùng loop result.
- Kết luận: spec đủ, implementation cover đủ AC.
