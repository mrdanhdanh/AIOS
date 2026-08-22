# TASK-093 Implementation

Behavioral Spec + ADR-0008 implementation:

- `aios/behavioral_docs/docs.py` — `BehavioralDoc`, `BehavioralDocReviewer`,
  `DocReviewResult` (doc review/validation helper).
- `aios/behavioral_docs/tests/test_docs.py` — 6 doc-review tests.
- `docs/behavioral_spec.md` — Behavioral Spec covering T089-T092.
- `docs/adr/ADR-0008.md` — Behavioral Conformance ADR (rationale + integration map).

Integration (reference-level, no rewrite):
- `docs/` + ADR convention (T071 DX)
- chuỗi T089 (`aios/behavioral`) → T090 (`aios/harness_coverage`) → T091
  (`aios/meta_harness`) → T092 (`aios/readiness_trust`)
