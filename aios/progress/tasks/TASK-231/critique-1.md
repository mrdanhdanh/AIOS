# TASK-231 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ code được ghi qua `RealToolHandler` (không ghi trực tiếp bằng `open()`) để qua PermissionBroker + deny-list.
- Chưa chỉ định `verification_report` trả về gì.

## Rủi ro
- Ghi file trực tiếp → bypass policy (vi phạm nguyên tắc M30).

## Đề xuất
- `execute_code` ghi file qua `handler(write_step)` (scope WRITE), tùy chọn chạy test (scope EXECUTE).
- Trả `verification_report` string tóm tắt write/test.
- Fail-closed nếu không inject handler hoặc thiếu permission.
