# TASK-087 — Compatibility Conformance

## Objective
Xây dựng **Compatibility Conformance** — bộ kiểm tra xác nhận một build AIOS 1.x
**conform** với compatibility baseline (T084) và backward-compat guarantee (T086),
sinh conformance report có evidence. TASK-087 là **conformance harness**, không
phải feature mới (dựa trên Certification T073 + Contract T064).

## Scope
**In scope:** `aios/conformance/` — ConformanceCheck, ConformanceReport,
ConformanceRunner. Tích hợp Certification (T073) + Contract (T064) + Version (T084)
+ Backward (T086).
**Out of scope:** thay thế certifier; provider/filesystem adapters.

## Deliverables
- `aios/conformance/conformance.py` — runner + report + gate + certify.
- `aios/conformance/tests/test_conformance.py` — 7 tests (Test Matrix).
- Tích hợp Certification (T073) + Contract (T064) + Version (T084) + Backward (T086).

## Acceptance Criteria
- Mọi compat check (T086) chạy trong conformance.
- Version policy (T084) + contract freeze (T064) chạy.
- Một check FAIL → không conform (fail-closed).
- Report có provenance đầy đủ.
- Cùng build + suite → cùng kết quả (deterministic).
- Tích hợp Certification + Contract + Version + Backward.
- Regression milestone trước PASS; không vi phạm invariants.

## Dependencies
- T086 (Backward Compat) → T087 → T088.
- T073 (Certification), T064 (Contract), T084 (Version), T086 (Backward).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `conformance` là `unknown`
  layer; import stdlib + `aios.backward_compat.backward` (T086) + `aios.contracts.contract` (T064) + `aios.versioning.versioning` (T084) + `aios.certification.certifier` (T073).
