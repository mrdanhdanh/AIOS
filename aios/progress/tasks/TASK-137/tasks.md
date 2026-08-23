# TASK-137 — Task Breakdown

1. Định nghĩa `WorkspaceStatus` (active/archived) + `WorkspaceRecord` (immutable `workspace_id`).
2. Định nghĩa `SnapshotRecord` (immutable `snapshot_id`, `state_hash`).
3. `WorkspaceManager.create` với duplicate-id guard (T001 Rule 1).
4. `snapshot` fail-closed yêu cầu state không rỗng, sinh `state_hash` (T078).
5. `restore` trả về `state_hash` (T020/T066); `archive`.
6. `provenance()` với `content_hash` (T001/T078).
7. Tests (`test_workspace.py`): 8 tests.
8. Chạy pytest + gate_check.
