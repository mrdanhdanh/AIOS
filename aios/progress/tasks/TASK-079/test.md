# Test — TASK-079

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| replay cùng input + verifier | cùng verdict (deterministic) | PASS |
| replay khác original | flag non-determinism | PASS |
| replay unknown run | raise ReplayError | PASS |
| recorded inputs hash | stable (same input → same hash) | PASS |
| cùng input + verifier (2x) | cùng verdict + hash | PASS |

`python -m pytest aios/replay -q` → 5 passed.
