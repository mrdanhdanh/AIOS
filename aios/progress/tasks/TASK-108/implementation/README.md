# TASK-108 Implementation

Management Console / Independent Harness Integration lives in:

- `aios/independent_harness/console.py` — `ConsoleHarnessView`, `ManagementConsoleIntegration`.
- `aios/api/routers/independent_harness.py` — REST boundary (register/status/action), included in `aios/api/app.py`.
- `aios/dashboard/views.py` — `IndependentHarnessView` (View 11).
- Tests trong `aios/independent_harness/tests/test_independent_harness.py` (Test Matrix T108).

Integration (import-level, no rewrite):
- `aios.independent_harness.foundation` (HarnessRegistry, PolicyAuthority) — T104
- `aios.independent_harness.oracle` (OracleResult, IndependentVerificationOracle) — T105
- `aios.independent_harness.behavioral_bridge` (BehavioralConformanceReport) — T106
- `aios.independent_harness.permission_sandbox_bridge` (PermissionSandboxReport) — T107
- `aios.dashboard.views` — T042/T072/T018
- `aios.api` (routers) — T017
