# Test Matrix — TASK-101

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| change xảy ra | trigger cert | test_change_triggers_cert |
| mọi gate PASS | deploy allowed | test_all_gates_pass_deploy_allowed |
| 1 gate FAIL | không deploy (fail-closed) | test_one_gate_fail_blocks_deploy |
| cert chạy lại mỗi change | không bỏ qua | test_cert_reruns_on_each_change |
| cùng change + suite | cùng result (deterministic) | test_deterministic_cert_result |
| cert evidence | provenance đầy đủ | test_cert_evidence_provenance |

6 tests, all passing.
