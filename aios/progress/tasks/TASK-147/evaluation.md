# TASK-147 — Evaluation

## Acceptance Criteria verification
- [x] Taxonomy xác định, đóng — test `test_closed_taxonomy`.
- [x] Observation (T146) → class xác định — test `test_classify_clear_trace`.
- [x] UNKNOWN (confidence thấp) → không promote PASS (T078) — test `test_classify_ambiguous_trace_unknown`.
- [x] Mọi classification có provenance (T001 Rule 5) — test `test_classify_requires_provenance`.
- [x] Cùng observation → cùng class (deterministic) — test `test_deterministic_same_observation_same_class`.
- [x] Tích hợp Execution Observation + Execution Contract + Evidence.
- [x] Regression milestone trước PASS.

**Verdict:** Tất cả AC PASS. UNKNOWN không được nâng thành PASS. Evidence có provenance.
