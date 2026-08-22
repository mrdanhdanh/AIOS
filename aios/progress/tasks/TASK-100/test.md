# Test Matrix — TASK-100

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| failure từ T094/T099 | thu thập vào corpus | test_failure_collected_from_t094 |
| corpus dedupe | không trùng lặp | test_corpus_dedupe_no_duplicate |
| gap chưa covered | report (T090) | test_gap_uncovered_reported |
| improvement đề xuất | harness/detection/remediation | test_improvement_proposed |
| cùng failure + corpus | cùng analysis (deterministic) | test_deterministic_analysis |
| corpus entry evidence | provenance đầy đủ | test_corpus_entry_evidence_provenance |

6 tests, all passing.
