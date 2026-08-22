# Test Matrix — TASK-102

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| action tiêu budget | remaining giảm đúng | test_action_consumes_budget |
| budget cạn | SAFE-STOP (T068) | test_budget_empty_triggers_safe_stop |
| action vượt remaining | BLOCK (T054/T067) | test_action_exceeding_remaining_blocked |
| autonomy level cao | budget policy khác | test_autonomy_level_couples_budget |
| cùng action + budget | cùng consume (deterministic) | test_deterministic_consume |
| budget change evidence | provenance đầy đủ | test_budget_evidence_provenance |

6 tests, all passing.
