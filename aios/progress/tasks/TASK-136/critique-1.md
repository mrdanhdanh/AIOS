# TASK-136 — Critique 1

## Missing / risky sections
- Cần enforce `sandbox_id` immutable + không tái sử dụng (T001 Rule 1).
- `isolate` phải yêu cầu `policy_ref` (T113 boundary) trước khi isolate.
- `is_usable` phải kết hợp status ISOLATED + health healthy.

## Risks
- Nếu sandbox không isolate được mà vẫn chạy execution -> vi phạm T040.
- Thiếu provenance trên destroy -> không trace được lifecycle.

## Verdict
SPEC acceptable; cần fail-closed isolate + immutable id.
