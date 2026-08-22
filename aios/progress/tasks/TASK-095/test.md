# Test Matrix — TASK-095

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| diagnosis -> candidates | sinh đủ | test_generate_from_diagnosis |
| risk score | evidence-based | test_risk_score_evidence_based |
| candidate vi phạm policy | bị loại (fail-closed) | test_policy_violation_removed |
| cùng diagnosis + policy | cùng ranking (deterministic) | test_deterministic_ranking |
| candidate evidence | provenance đầy đủ | test_candidate_provenance |
| ranked output | risk thấp trước | test_ranked_low_risk_first |
| full flow | plan compliant | test_engine_full_flow_plan |

7 tests, all passing.
