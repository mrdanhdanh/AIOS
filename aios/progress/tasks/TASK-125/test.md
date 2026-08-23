# Test — TASK-125

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| agent I/O-free | capability-injected OK | `test_agent_io_free_capability_injected_ok` |
| agent không I/O-free | reject | `test_agent_must_be_io_free` |
| agent_id rỗng | reject | `test_agent_id_required` |
| transition hợp lệ | OK | `test_valid_transition_chain`, `test_reviewing_to_done_direct` |
| transition thiếu artifact | REJECT (T001 Rule 6) | `test_transition_missing_artifact_rejects` |
| transition bị policy reject | REJECT (T113) | `test_transition_policy_rejected` |
| transition bất hợp lệ | REJECT | `test_illegal_transition_rejects` |
| cùng state + artifact | cùng transition (deterministic) | `test_deterministic_same_state_artifact` |
| transition evidence | provenance đầy đủ (T001) | `test_transition_evidence_provenance` |
| module không import forbidden | BLOCK (ARCH-001..004) | `test_module_has_no_forbidden_imports` |
| module là unknown layer | classify = unknown | `test_contract_module_path_is_unknown_layer` |

## Command
```
python -m pytest aios/coder/tests/test_coder.py -q
```
Kết quả: 12 passed.
