# Test Matrix — TASK-089

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| scenario conform | PASS | test_scenario_conform_pass |
| behavior lệch expected | không conform (fail-closed) | test_behavior_deviation_not_conform_fail_closed |
| spec không observable | bị chặn | test_non_observable_spec_blocked |
| cùng scenario + system | cùng observable (deterministic) | test_same_scenario_deterministic |
| behavior evidence | provenance đầy đủ | test_behavior_evidence_provenance |
| behavior harness chạy | observe được | test_harness_verify_returns_verdict / test_replay_check_reproduces |
| conformance suite fail-closed | không conform | test_conformance_suite_fail_closed |
| conformance suite pass + report | conformant + report | test_conformance_suite_pass_and_report |

9 tests, all passing.
