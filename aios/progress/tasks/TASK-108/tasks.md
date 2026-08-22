# Breakdown — TASK-108

1. `ConsoleHarnessView` dataclass — `console_id, harness_status, independent_results_summary, aios_authority_flag="aios", operator_action, evidence_ref`.
2. `ManagementConsoleIntegration.aggregate` — tổng hợp T105/T106/T107 → view (fail-closed).
3. `ManagementConsoleIntegration.request_operator_action` — policy-gated, dispatch qua API/runtime.
4. `aios/api/routers/independent_harness.py` — register/status/action; include trong `app.py`.
5. `aios/dashboard/views.py` — `IndependentHarnessView` (View 11).
6. Tests (5) theo Test Matrix T108.
7. Tích hợp Oracle + Foundation + Bridges + Dashboard + API.
