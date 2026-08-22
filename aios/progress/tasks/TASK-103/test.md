# Test Matrix — TASK-103

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| decision vi phạm constitution | BLOCK (fail-closed) | test_violation_blocks |
| audit entry ghi | immutable chain đúng | test_audit_chain_immutable |
| sửa audit entry | phát hiện tamper (T078) | test_tamper_detected |
| decision trace | principal + policy rõ | test_decision_trace_principal_policy |
| cùng decision + constitution | cùng compliance (deterministic) | test_deterministic_compliance |
| audit evidence | provenance đầy đủ | test_audit_evidence_provenance |

6 tests, all passing.
