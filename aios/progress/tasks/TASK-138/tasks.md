# TASK-138 — Task Breakdown

1. Định nghĩa `ResourceLimit` (cpu/mem, positive guard T039) + `Decision` (allow/deny).
2. Định nghĩa `ExecutionPolicy` (resource_limit/network_egress/command_allowlist).
3. Định nghĩa `PolicyDecision` + `content_hash`.
4. `PolicyEngine.register` với duplicate-id guard (T001 Rule 1).
5. `evaluate` fail-closed: cpu/mem/egress/command -> deny (T078/T039/T040).
6. `provenance()` với `content_hash` (T001/T078).
7. Tests (`test_policy.py`): 8 tests.
8. Chạy pytest + gate_check.
