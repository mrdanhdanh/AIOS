# Test Matrix — TASK-104

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| đăng ký harness mới | `harness_id` immutable, OK | test_register_new_harness_ok |
| đăng ký `harness_id` trùng | REJECT (T001 Rule 1) | test_register_duplicate_id_rejected |
| ingest evidence thiếu hash | reject (fail-closed, T078) | test_ingest_missing_hash_rejected |
| ingest evidence có provenance | OK, ghi nhận | test_ingest_with_provenance_ok |
| independent harness ghi đè policy | bị chặn (authority AIOS) | test_independent_harness_cannot_override_policy |
| cùng adapter + input | cùng kết quả (deterministic) | test_same_adapter_and_input_deterministic |

6 tests, all passing.
