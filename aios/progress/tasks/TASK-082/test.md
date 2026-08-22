# Test — TASK-082

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| creative asset có provenance | accept + route | PASS |
| asset thiếu vendor provenance | reject (fail-closed) | PASS |
| reference thay đổi không approval | bị chặn | PASS |
| license vi phạm | reject | PASS |
| cùng asset + reference | cùng so sánh (deterministic) | PASS |
| creative asset evidence | provenance (evidence_ref) | PASS |
| creative capability registry | register/guard type | PASS |

`python -m pytest aios/creative_domain -q` → 7 passed.
