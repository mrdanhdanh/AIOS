# Test — TASK-080

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| capture UI state | hash sinh đúng (deterministic) | PASS |
| diff vượt ngưỡng | flag regression (không PASS) | PASS |
| baseline thay đổi không approval | bị chặn | PASS |
| cùng UI state + config | cùng hash | PASS |
| visual evidence gắn provenance | evidence_ref present | PASS |
| replay visual (baseline) | evaluate với baseline | PASS |

`python -m pytest aios/visual_evidence -q` → 6 passed.
