# Critique 1 — TASK-100

- Spec cần làm rõ corpus fail-closed gap: gap chưa covered phải được report, không giấu (T090).
- Corpus phải deduplicated bằng content_hash (T001 Rule 5) — không duplicate, không silent drop.
- Mọi entry ghi Evidence (T001 Rule 5) qua EvidenceStore.
- Tích hợp Detect (T094) + Loop (T099) để thu thập failure.
- Đề xuất test deterministic: cùng failure + corpus → cùng analysis.
- Kết luận: spec đủ, implementation cover đủ AC.
