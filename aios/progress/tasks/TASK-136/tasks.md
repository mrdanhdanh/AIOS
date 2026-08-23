# TASK-136 — Task Breakdown

1. Định nghĩa `IsolationLevel` (process/fs/network) + `SandboxStatus` (created/isolated/destroyed).
2. Định nghĩa `SandboxRecord` (immutable `sandbox_id`).
3. `SandboxManager.create` với duplicate-id guard (T001 Rule 1).
4. `isolate` fail-closed yêu cầu `policy_ref` (T113).
5. `healthcheck` / `destroy` / `is_usable` (ISOLATED + healthy).
6. `provenance()` với `content_hash` (T078/T001).
7. Tests (`test_sandbox.py`): 8 tests.
8. Chạy pytest + gate_check.
