# TASK-084 — Version + Compatibility Baseline

## Objective
Thiết lập **Version + Compatibility Baseline** — quy ước versioning (semver) và
chính sách tương thích cho AIOS 1.x, làm nền tảng cho mọi task compatibility sau
(T085-T088). TASK-084 là **versioning policy + baseline**, không phải feature mới
(dựa trên Contract Freeze T064).

## Scope
**In scope:** `aios/versioning/` — VersionPolicy, ChangeType, VersionBump,
VersionChange, VersionDecision, VersionBaseline, CompatibilityMatrix,
VersionPolicyEngine. Tích hợp Contract Freeze (T064) + Migration (T074).
**Out of scope:** thay thế contract; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/versioning/versioning.py` — policy + matrix + engine.
- `aios/versioning/tests/test_versioning.py` — 9 tests (Test Matrix).
- Tích hợp với Contract (T064) + Migration (T074) + Baseline ADR.

## Acceptance Criteria
- Semver policy định nghĩa rõ MAJOR/MINOR/PATCH.
- Breaking change → MAJOR + ADR + deprecation window.
- Compatibility matrix 1.0 ↔ 1.x được định nghĩa.
- Mọi version change có provenance (T001 Rule 5).
- Cùng change type → cùng version bump (deterministic).
- Tích hợp được với Contract (T064) + Migration (T074).
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T083 (SkillDistiller) → T084 → T085.
- T064 (Contract Freeze), T074 (Upgrade/Migration).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `versioning` là `unknown`
  layer; chỉ import stdlib + `aios.contracts.contract` (T064).
