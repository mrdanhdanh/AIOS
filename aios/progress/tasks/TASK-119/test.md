# Test Matrix — TASK-119

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| extract edges | node + edge đúng | test_t119_extract_edges |
| cycle detected | BLOCK (T001 Rule 2) | test_t119_cycle_detected_blocks |
| node hash | content_hash + provenance (T001) | test_t119_node_hash_and_evidence |
| graph secret | không lộ (T040) | test_t119_secret_not_graph |
| cùng source | cùng graph (deterministic) | test_t119_deterministic |
| graph evidence | provenance đầy đủ (T001) | test_t119_evidence_provenance |

6 tests, all passing.
