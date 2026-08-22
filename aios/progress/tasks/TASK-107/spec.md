# TASK-107 — Permission + Sandbox Bridge

## Objective
Xây **Permission + Sandbox Bridge** — bridge các permission/sandbox check từ independent harness vào AIOS verification mà không phá Core. Bridge quyền + sandbox, không phải feature mới (dựa trên Oracle T105 + Foundation T104 + Identity/RBAC T035 + Sandbox Isolation T040 + Credential/Permission/Policy T113).

## Scope
**In scope:** `aios/independent_harness/permission_sandbox_bridge.py` — `PermissionSandboxReport`, `PermissionSandboxBridge` + tests. Tích hợp Oracle (T105) + Foundation (T104) + Identity (T035) + Sandbox (T040) + Credential (T113).
**Out of scope:** permission/sandbox feature mới; provider/filesystem adapters.

## Deliverables
- `aios/independent_harness/permission_sandbox_bridge.py` — check → AIOS policy result (6 tests).
- Tests Test Matrix T107.
- Tích hợp Oracle (T105) + Foundation (T104) + Identity (T035) + Sandbox (T040) + Credential (T113).

## Acceptance Criteria
- Permission + sandbox check được bridge từ independent harness vào AIOS.
- `aios_policy_result` do AIOS quyết; independent result không override (authority AIOS).
- Result không xác định → INCONCLUSIVE → không promote PASS (T078).
- Mọi bridge có provenance (T001 Rule 5).
- Cùng check + input → cùng `aios_policy_result` (deterministic).
- Tích hợp được với Oracle + Foundation + Identity + Sandbox + Credential.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T104, T105 → T107 → T108.
- T035 (Identity), T040 (Sandbox), T113 (Credential), T078 (Integrity), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. `independent_harness` là `unknown` layer.
