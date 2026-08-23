# Test Matrix — TASK-122

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| build context | assembly từ T121 OK | test_t122_build_context |
| vượt budget | trim hoặc reject (T024) | test_t122_over_budget_trim |
| priority trim | cắt đúng priority | test_t122_priority_trim_keeps_high |
| chunk hash | content_hash + provenance (T001) | test_t122_chunk_hash_and_evidence |
| cùng retrieval + budget | cùng context (deterministic) | test_t122_deterministic |
| build secret | không lộ (T040) | test_t122_secret_not_built |

6 tests, all passing.
