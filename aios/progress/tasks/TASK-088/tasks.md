# Task Breakdown — TASK-088

- [x] CompatDoc dataclass (doc_id, covers, adr_ref, rationale, status, evidence_ref, references).
- [x] DocStatus enum (DRAFT/PUBLISHED/DEPRECATED).
- [x] DocReviewResult dataclass (approved, missing_coverage, missing_rationale, stale, broken_references).
- [x] CompatDocReviewer.review (fail-closed: coverage/rationale/stale/ref).
- [x] CompatDocReviewer.validate_references (no 404).
- [x] CompatDocReviewer.review_hash / provenance_complete.
- [x] ADR-Compatibility.md (policy + rationale).
- [x] Guides: versioning / migration / backward-compat / conformance.
- [x] Tests 7 cases (Test Matrix).
- [x] Tích hợp Docs + DX (T071) + T084-T087.
