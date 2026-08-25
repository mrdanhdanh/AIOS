# TASK-228 — Critique 1

## Thiếu sót trong spec
- Spec chưa nêu rõ `policy_ref` / `permission` / `evidence_ref` phải nằm ở đâu trong `ExecutionPlan` (step metadata hay plan metadata).
- Chưa chỉ định converter 2 chiều có cần giữ `cwd` khi round-trip hay không.
- Chưa có AC về tính lossless của round-trip.

## Rủi ro
- Nếu `aiagent execute` và `aiagent task` sinh `ExecutionPlan` khác cấu trúc → Flow A ∧ Flow B không hội tụ (mục tiêu M29 thất bại).
- Thiếu `evidence_ref` → không gắn được provenance chain về sau (M32).

## Đề xuất
- Chuẩn hóa: `policy_ref` + `permission` nằm trong `step.metadata`; `policy_ref` + `permissions` nằm trong `plan.metadata`.
- Round-trip `from_execution_plan` phải giữ `id`, `command`, `cwd`, `permissions` (lossless cho trường được kiểm soát).
- Thêm test round-trip lossless.
