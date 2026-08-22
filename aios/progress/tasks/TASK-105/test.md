# Test Matrix — TASK-105

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| map invariant -> oracle check | OK | test_map_invariant_to_oracle_check |
| bridge evidence oracle vào AIOS | ghi nhận, có provenance | test_evidence_bridged_into_aios |
| oracle conflict với AIOS policy | AIOS authoritative, không override | test_aios_authority_not_overridden_by_oracle |
| oracle verdict INCONCLUSIVE | không promote PASS (T078) | test_oracle_inconclusive_not_promoted |
| oracle không xác định (UNKNOWN) | fail-closed | test_oracle_unknown_fail_closed |
| cùng invariant + oracle input | cùng verdict (deterministic) | test_same_invariant_and_input_deterministic |

6 tests, all passing.
