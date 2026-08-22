# Test — TASK-081

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| asset validate OK | route đến capability đúng | PASS |
| asset không validate | không route (fail-closed) | PASS |
| asset type không có capability | bị chặn | PASS |
| asset content_hash | khớp | PASS |
| cùng asset type + registry | cùng route (deterministic) | PASS |
| asset evidence | provenance (evidence_ref) | PASS |
| schema required_fields | validate | PASS |

`python -m pytest aios/asset_pipeline -q` → 7 passed.
