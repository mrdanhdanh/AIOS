# TASK-236 — Critique 2

## Thiếu sót
- Cần đảm bảo mỗi phase ghi `trace` để provenance (Rule 5).
- Cần test deterministic (cùng input → cùng remediation_id/phase).

## Rủi ro
- Thiếu audit trail → integrity gate fail (T078 yêu cầu audit_trail).

## Đề xuất
- Mỗi bước append vào `trace`; truyền `trace` vào `integrity.check(audit_trail=trace)`.
- Thêm test `test_lifecycle_deterministic_same_inputs`.
