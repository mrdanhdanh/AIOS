# Critique 1 — TASK-221

## Findings
- Chưa định nghĩa response có bao gồm `steps` dạng list hay chỉ summary → bổ sung `steps` (name/status/detail).
- GET endpoint cần store; nên dùng dict in-memory đơn giản (không cần DB ở prototype).
- Cần xử lý `objective` bắt buộc, các field khác optional.

## Verdict
REVISE — bổ sung các điểm trên.
