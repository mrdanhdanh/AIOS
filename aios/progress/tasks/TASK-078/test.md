# Test — TASK-078

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| evidence hash khớp | verify PASS | PASS |
| evidence bị sửa | reject (fail-closed) | PASS |
| verifier version đổi | đánh dấu, không so sánh sai | PASS |
| verdict UNKNOWN | không promote PASS | PASS |
| verdict INCONCLUSIVE | không promote PASS | PASS |
| cùng evidence + verifier | cùng verdict (deterministic) | PASS |
| provenance incomplete | không complete | PASS |
| tamper + provenance | report đầy đủ | PASS |

`python -m pytest aios/verification_integrity -q` → 8 passed.
