# TASK-141 — Critique 1

## Missing / risky sections
- `capture_output` phải redact secret trước khi lưu (T040/T113).
- `content_hash` phải rỗng khi không có output/artifact (fail-closed, T078).
- `collector_id` immutable (T001 Rule 1).

## Risks
- Nếu secret không redact -> lộ thông tin nhạy cảm (T040).
- Nếu artifact rỗng mà vẫn hash -> mất integrity gate.

## Verdict
SPEC acceptable; cần secret isolation + fail-closed hash.
