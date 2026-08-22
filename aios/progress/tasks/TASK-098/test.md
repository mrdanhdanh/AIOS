# Test Matrix — TASK-098

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| artifact hash khớp | integrity PASS | test_integrity_pass_matching_hashes |
| artifact bị sửa | reject (fail-closed) | test_tampered_artifact_rejected |
| kill switch trong remediation | dừng (T068) | test_kill_switch_halts_remediation |
| audit trail thiếu | bị chặn | test_missing_audit_trail_rejected |
| cùng artifact + check | cùng result (deterministic) | test_deterministic_integrity |
| integrity evidence | provenance đầy đủ | test_provenance_complete |

6 tests, all passing.
