# Test Matrix — TASK-092

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| ready + trusted | certify (READY_TRUSTED) | test_ready_and_trusted_certifies |
| ready + untrusted | KHÔNG certify (fail-closed) | test_ready_but_untrusted_not_certified_fail_closed |
| not ready + trusted | KHÔNG certify | test_not_ready_but_trusted_not_certified |
| trust decision evidence | provenance đầy đủ | test_trust_decision_evidence_provenance |
| cùng system + harness | cùng trust (deterministic) | test_same_system_same_trust_deterministic |
| combined gate chạy | đúng logic | test_combined_gate_logic |

6 tests, all passing.
