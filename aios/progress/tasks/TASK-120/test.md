# Test Matrix — TASK-120

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| build hybrid index | symbol + dep + embedding OK | test_t120_build_hybrid |
| hybrid query | rank kết hợp đúng | test_t120_hybrid_query_ranked |
| embedding fail | reject (fail-closed) | test_t120_embedding_fail_reject |
| index secret | không index (T040) | test_t120_secret_not_embedded |
| cùng query + index | cùng rank (deterministic) | test_t120_deterministic |
| index evidence | provenance đầy đủ (T001) | test_t120_evidence_provenance |

6 tests, all passing.
