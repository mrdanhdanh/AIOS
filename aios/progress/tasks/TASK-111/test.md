# Test Matrix — TASK-111

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| đăng ký model | model_id immutable OK | test_t111_register_immutable_id |
| đăng ký id trùng | REJECT (T001 Rule 1) | test_t111_duplicate_id_rejected |
| resolve theo rule | LLM call = 0, deterministic | test_t111_resolve_deterministic_no_llm |
| cùng request + policy | cùng selected_model | test_t111_resolve_deterministic_no_llm |
| không resolve được | reject (fail-closed) | test_t111_unresolved_fail_closed |
| resolve evidence | provenance đầy đủ (T001) | test_t111_resolve_provenance |

6 tests, all passing.
