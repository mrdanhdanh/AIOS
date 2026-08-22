# TASK-086 — Backward Compatibility

## Objective
Đảm bảo **Backward Compatibility** — hệ thống 1.x tiếp tục phục vụ consumer viết
cho 1.0 mà không break (API/schema/event không đổi breaking). TASK-086 là
**compat guarantee**, không phải feature mới (dựa trên Contract Freeze T064 +
Version Baseline T084).

## Scope
**In scope:** `aios/backward_compat/` — CompatSurface, CompatCheck, CompatResult,
CompatSuiteResult, BackwardCompatChecker, CompatTestSuite. Tích hợp Contract
(T064) + Version Baseline (T084) + Migration (T085).
**Out of scope:** thay thế contract; provider/filesystem adapters.

## Deliverables
- `aios/backward_compat/backward.py` — checker + suite.
- `aios/backward_compat/tests/test_backward.py` — 7 tests (Test Matrix).
- Tích hợp Contract (T064) + Version (T084) + Migration (T085).

## Acceptance Criteria
- 1.0 consumer vẫn hoạt động trên 1.x (API/schema/event).
- Breaking change với 1.0 consumer → BLOCK (phải MAJOR + deprecation T084).
- Compat test suite PASS trước DONE.
- Mọi compat check có provenance (T001 Rule 5).
- Cùng surface + version → cùng kết quả (deterministic).
- Tích hợp Contract + Version + Migration.
- Regression milestone trước PASS; không vi phạm invariants.

## Dependencies
- T085 (Migration) → T086 → T087.
- T064 (Contract Freeze), T084 (Version Baseline).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `backward_compat` là `unknown`
  layer; import stdlib + `aios.contracts.contract` (T064) + `aios.versioning.versioning` (T084).
