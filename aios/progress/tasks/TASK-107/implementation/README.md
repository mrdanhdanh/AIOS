# TASK-107 Implementation

Permission + Sandbox Bridge lives in `aios/independent_harness/`:

- `aios/independent_harness/permission_sandbox_bridge.py` — `PermissionSandboxReport`, `PermissionSandboxBridge`.
- Tests trong `aios/independent_harness/tests/test_independent_harness.py` (Test Matrix T107).

Integration (import-level, no rewrite):
- `aios.independent_harness.foundation` (HarnessRegistry, EvidenceIngestBoundary, PolicyAuthority) — T104
- `aios.independent_harness.oracle` (IndependentVerificationOracle) — T105
- `aios.identity.contracts` (Permission, Principal) — T035/T113
- `aios.security.contracts` (SandboxConfig, NetworkPolicy) — T040
- `aios.security.isolation` (IsolationManager) — T040
- `aios.verification_integrity` (VerdictClass) — T078
