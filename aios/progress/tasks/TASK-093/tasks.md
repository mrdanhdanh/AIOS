# Task Breakdown — TASK-093

- [x] DocStatus enum (PUBLISHED / DRAFT).
- [x] BehavioralDoc dataclass (doc_id / covers / adr_ref / status / references / rationale / evidence).
- [x] DocReviewResult dataclass (covers_m13 / adr_has_rationale / no_stale / links_valid / deterministic / passed).
- [x] BehavioralDocReviewer.review (fail-closed: coverage + rationale + no-stale).
- [x] BehavioralDocReviewer._exists (no 404 / no stale).
- [x] BehavioralDocReviewer.provenance_complete / review_hash.
- [x] docs/behavioral_spec.md (covers T089-T092).
- [x] docs/adr/ADR-0008.md (rationale + integration map).
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Docs + DX (T071) + chuỗi T089-T092 (import-level / reference).
