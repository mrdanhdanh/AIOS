# TASK-233 — Breakdown

## Sub-tasks
1. **T233.1** — Tạo `aios/autonomous_loop/lifecycle.py`: `UnifiedAutonomousLifecycle` wrap `LoopController`.
2. **T233.2** — Tích hợp `RetryGuard` (sig cố định per goal) + `KillSwitch` (fail-closed halt).
3. **T233.3** — Test: run qua loop / halt dưới killswitch / retryguard autostop.
4. **T233.4** — Architecture gate + pytest.

## Verification
`pytest aios/autonomous_loop/tests/test_autonomous_loop.py -k unified` + `pytest aios/governance/architecture`.
