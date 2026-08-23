# Test Matrix — TASK-118

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| parse source | symbol đúng (name/kind/location) | test_t118_parse_symbols |
| symbol hash | content_hash + provenance (T001) | test_t118_symbol_hash_and_evidence |
| parse fail | reject (fail-closed) | test_t118_parse_fail_reject |
| lookup symbol | trả đúng kết quả | test_t118_lookup |
| cùng source | cùng symbol set (deterministic) | test_t118_deterministic |
| index secret | không lộ (T040) | test_t118_secret_not_indexed |

6 tests, all passing.
