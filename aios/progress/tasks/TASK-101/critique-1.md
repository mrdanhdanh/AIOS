# Critique 1 — TASK-101

- Spec cần làm rõ cert fail-closed deploy: một gate FAIL → không deploy.
- Mọi change phải trigger cert (T062/T099), không bỏ qua.
- Mọi cert run ghi Evidence (T001 Rule 5) qua EvidenceStore.
- Tích hợp Certification (T073) + Conformance (T087) + Harness trust (T090/T091).
- Đề xuất test deterministic: cùng change + suite → cùng cert result.
- Kết luận: spec đủ, implementation cover đủ AC.
