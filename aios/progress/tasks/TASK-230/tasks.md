# TASK-230 — Breakdown

## Sub-tasks
1. **T230.1** — Thêm `CoderCapabilityResolver(contract, registry)` trong `aios/coder/contract.py`.
2. **T230.2** — `resolve(capability)`: fail-closed nếu không `can_inject` hoặc không có trong registry.
3. **T230.3** — Test: resolve thành công / không khai báo / không đăng ký.
4. **T230.4** — Architecture gate + pytest.

## Verification
`pytest aios/coder/tests/test_coder.py` + `pytest aios/governance/architecture`.
