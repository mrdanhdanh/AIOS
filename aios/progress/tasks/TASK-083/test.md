# Test — TASK-083

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| distill workflow | skill có contract 1.0 | PASS |
| skill không conform 1.0 | bị chặn (T064) | PASS |
| static deploy vi phạm guard | BLOCK (T063) | PASS |
| static package dynamic dep | bị chặn | PASS |
| cùng workflow + distiller | cùng skill (deterministic) | PASS |
| skill evidence | provenance (evidence_ref) | PASS |

`python -m pytest aios/skill_distiller -q` → 6 passed.
