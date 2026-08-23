# TASK-136 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| tạo sandbox | `sandbox_id` immutable OK | PASS |
| tạo id trùng | REJECT (T001 Rule 1) | PASS |
| sandbox không isolate | reject (T040) | PASS |
| sandbox unhealthy | không chạy execution | PASS |
| lifecycle event | provenance đầy đủ (T001) | PASS |
| cùng state | cùng result (deterministic) | PASS |

Run: `python -m pytest aios/execution/tests/test_sandbox.py -q` -> 8 passed.
