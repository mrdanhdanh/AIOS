# TASK-229 — Breakdown

## Sub-tasks
1. **T229.1** — Thêm `_governance_precheck(kernel, plan)`: chạy `PolicyEngine.evaluate` + `PermissionBroker.has` cho mỗi step (fail-closed).
2. **T229.2** — `--simulate` gọi `record_execution_evidence(..., simulated=True)` (Evidence SIMULATED, 0 OS exec).
3. **T229.3** — Real exec: chạy pre-check trước; tích hợp `RetryGuard` quanh kết quả FAILED.
4. **T229.4** — Test: pre-check deny/allow + simulate evidence. Chạy architecture gate + pytest.

## Verification
`pytest aios/cli/tests/test_execute.py` + `pytest aios/governance/architecture`.
