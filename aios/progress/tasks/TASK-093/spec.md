# TASK-093 — Behavioral Spec + ADR-0008

## Objective
Soạn **Behavioral Spec + ADR-0008** — chuẩn hóa tài liệu behavioral conformance
(T089) và quyết định kiến trúc liên quan thành ADR-0008, đóng gói toàn bộ chuỗi
M13. TASK-093 là **documentation + ADR, không phải code mới** (dựa trên Docs +
DX T071 + chuỗi T089-T092).

## Scope
**In scope:** `aios/behavioral_docs/` (doc review/validation helper) + `docs/behavioral_spec.md`
+ `docs/adr/ADR-0008.md` + reference DX (T071). Tích hợp Docs + DX (T071) + chuỗi T089-T092.
**Out of scope:** runtime feature mới; provider/filesystem adapters.

## Deliverables
- `aios/behavioral_docs/docs.py` — BehavioralDoc, BehavioralDocReviewer, DocReviewResult.
- `aios/behavioral_docs/tests/test_docs.py` — 6 tests (Test Matrix).
- `docs/behavioral_spec.md` (covers T089-T092).
- `docs/adr/ADR-0008.md` (behavioral conformance decision + rationale).
- Tích hợp Docs + DX (T071) + chuỗi T089-T092.

## Acceptance Criteria
- Docs cover đủ T089-T092.
- ADR-0008 ghi rationale rõ ràng.
- Doc khớp implementation đã DONE (không stale).
- Mọi doc reference có provenance (link task).
- Cùng nội dung → cùng review result (deterministic).
- Tích hợp được với Docs + DX + chuỗi M13.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T092 (System Readiness) → T093 → T094 (M14).
- T071 (DX), T089-T092.

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `behavioral_docs` là `unknown`
  layer; import stdlib + pathlib only.
