# TASK-237 — Test

- `test_aggregator_returns_all_14_planes`: 14 planes, status empty.
- `test_aggregator_collects_ok_plane`: collector ok -> data.
- `test_aggregator_isolates_plane_errors`: 1 plane lỗi -> error, others intact.
- `test_aggregator_deterministic`: cùng input -> cùng dict.
- `test_control_center_endpoint_returns_all_planes`: API trả đủ 14 planes.
- `test_control_center_is_read_only_snapshot`: system_health là string hợp lệ.

Kết quả: 6 passed.
