# TASK-234 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ `Evidence` cần thêm `requirement_id`/`freshness`/`coverage` và `EvidenceStore` cần `_coverage` map.
- Chưa chỉ định freshness TTL (đề xuất 1h).

## Rủi ro
- Nếu không có coverage map → M32 không đo được evidence theo requirement.

## Đề xuất
- Thêm field + `_coverage` + `coverage_map`/`is_requirement_covered`/`is_stale`.
- `record_execution_evidence` truyền `requirement_id` + `freshness` (1h TTL).
