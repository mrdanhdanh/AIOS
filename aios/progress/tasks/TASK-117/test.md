# Test Matrix — TASK-117

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| scan repo | file + metadata OK | test_t117_scan_repo_metadata |
| file không hash được | reject (fail-closed) | test_t117_unhashable_reject_fail_closed |
| change detection | new/modified/deleted đúng | test_t117_change_detection |
| scan secret file | không lộ (T040) | test_t117_secret_not_leaked |
| cùng repo state | cùng result (deterministic) | test_t117_deterministic |
| scan evidence | provenance đầy đủ (T001) | test_t117_evidence_provenance |

6 tests, all passing.
