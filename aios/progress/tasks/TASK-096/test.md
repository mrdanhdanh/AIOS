# Test Matrix — TASK-096

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| simulate PASS + meta PASS | gate PASS -> apply | test_simulate_pass_meta_pass_gate_pass |
| simulate FAIL | REJECT (fail-closed) | test_simulate_fail_rejects |
| meta-verify FAIL | REJECT | test_meta_verify_fail_rejects |
| sandbox không isolated | bị chặn (isolation) | test_sandbox_isolation_blocks_non_isolated |
| cùng candidate + sandbox | cùng outcome (deterministic) | test_deterministic_outcome |
| simulation evidence | provenance đầy đủ | test_provenance_complete |
| result fields | đầy đủ | test_simulation_result_fields |

7 tests, all passing.
