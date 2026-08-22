# Breakdown — TASK-107

1. `PermissionSandboxReport` dataclass — `check_id, permission_ref, sandbox_ref, independent_result, aios_policy_result, evidence_ref, authority="aios"`.
2. `PermissionSandboxBridge.bridge` — bridge check, tính `aios_policy_result` fail-closed, ghi provenance.
3. Tests (6) theo Test Matrix T107.
4. Tích hợp Oracle (T105) + Foundation (T104) + Identity (T035) + Sandbox (T040) + Credential (T113).
