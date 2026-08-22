# Test — TASK-087

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| mọi check PASS | cấp conformance | PASS |
| 1 check FAIL | KHÔNG conform (fail-closed) | PASS |
| version policy vi phạm | conform FAIL | PASS |
| contract không freeze | conform FAIL | PASS |
| report có evidence | provenance đầy đủ | PASS |
| cùng build + suite | cùng kết quả (deterministic) | PASS |
| certify chỉ khi conformant | CERTIFIED / None | PASS |

`python -m pytest aios/conformance -q` → 7 passed.
