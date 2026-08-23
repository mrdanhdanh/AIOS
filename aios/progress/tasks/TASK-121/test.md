# Test Matrix — TASK-121

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| query hybrid index | hits rank đúng | test_t121_query_hybrid |
| hit hash | content_hash + provenance (T001) | test_t121_hit_hash_and_evidence |
| query secret chunk | không trả (T040) | test_t121_secret_not_returned |
| index không sẵn sàng | reject (fail-closed) | test_t121_index_not_ready_reject |
| cùng query + index | cùng hits (deterministic) | test_t121_deterministic |
| retrieval evidence | provenance đầy đủ (T001) | test_t121_evidence_provenance |

6 tests, all passing.
