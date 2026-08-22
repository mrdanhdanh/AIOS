# Test Matrix — TASK-093

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| docs cover T089-T092 | PASS | test_docs_cover_m13_pass |
| ADR-0008 thiếu rationale | bị chặn | test_adr_missing_rationale_blocked |
| doc stale vs impl | bị chặn | test_stale_reference_blocked |
| doc link task | provenance đầy đủ | test_doc_link_provenance |
| cùng nội dung | cùng review (deterministic) | test_same_content_same_review_deterministic |
| doc reference valid | không 404 | test_missing_m13_coverage_blocked (coverage) + test_stale_reference_blocked (404) |

6 tests, all passing.
