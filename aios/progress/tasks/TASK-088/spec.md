# TASK-088 — Docs & ADR — Compatibility

## Objective
Soạn **Docs & ADR cho Compatibility** — tài liệu hóa đầy đủ chính sách tương
thích, quy trình versioning, backward-compat guarantee và conformance (T084-T087)
thành ADR + docs tham chiếu. TASK-088 là **documentation**, không phải code mới.

## Scope
**In scope:** `aios/compat_docs/` (doc review/validation helper) + `docs/adr/ADR-Compatibility.md`
+ guides (versioning / migration / backward-compat / conformance). Tích hợp Docs
+ DX (T071) + chuỗi T084-T087.
**Out of scope:** runtime feature mới; provider/filesystem adapters.

## Deliverables
- `aios/compat_docs/docs.py` — CompatDoc, CompatDocReviewer, DocReviewResult.
- `aios/compat_docs/tests/test_docs.py` — 7 tests (Test Matrix).
- `docs/adr/ADR-Compatibility.md` (policy + rationale).
- Guides: versioning / migration / backward-compat / conformance.
- Tích hợp Docs + DX (T071) + T084-T087.

## Acceptance Criteria
- Docs cover đủ T084-T087.
- ADR ghi rationale rõ ràng.
- Doc khớp với implementation đã DONE (không stale).
- Mọi doc reference có provenance (link task).
- Cùng nội dung → cùng review result (deterministic).
- Tích hợp Docs + DX + chuỗi compatibility.
- Regression milestone trước PASS; không vi phạm invariants.

## Dependencies
- T087 (Conformance) → T088 → T089 (M13).
- T071 (DX), T084-T087.

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `compat_docs` là `unknown`
  layer; import stdlib + reference T084-T087 (import-level).
