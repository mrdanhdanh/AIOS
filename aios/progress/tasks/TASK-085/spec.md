# TASK-085 — Migration 1.0 → 1.1

## Objective
Xây dựng **Migration 1.0 → 1.1** — kế hoạch và công cụ migrate hệ thống từ 1.0
sang 1.1 an toàn, reversible và có evidence, tuân thủ Version + Compatibility
Baseline (T084). TASK-085 là **version migration**, không phải runtime feature
(dựa trên Upgrade/Migration T074).

## Scope
**In scope:** `aios/migration/` — MigrationStep, MigrationPlan, MigrationState,
DryRunResult, MigrationResult, RollbackResult, MigrationRunner. Tích hợp Upgrade
(T074) + Version Baseline (T084) + Harness (T032).
**Out of scope:** thay thế upgrade engine; provider/filesystem adapters.

## Deliverables
- `aios/migration/migration.py` — detect/plan/dry-run/apply/rollback.
- `aios/migration/tests/test_migration.py` — 8 tests (Test Matrix).
- Tích hợp Upgrade (T074) + Version (T084) + Harness (T032).

## Acceptance Criteria
- Detect đúng hệ thống 1.0.
- Verify FAIL → không apply (fail-closed).
- Mọi bước reversible (có `down`).
- Dry-run không mutate.
- Mọi bước ghi evidence (T001 Rule 5).
- Cùng plan + state → cùng kết quả (deterministic).
- State migrate an toàn (T066).
- Tích hợp Upgrade + Version Baseline + Harness.
- Regression milestone trước PASS; không vi phạm invariants.

## Dependencies
- T084 (Version Baseline) → T085 → T086.
- T074 (Upgrade/Migration), T032 (Harness), T066 (Durable).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `migration` là `unknown`
  layer; import stdlib + `aios.upgrade.migration_plan` (T074) + `aios.harness.verification` (T032) + `aios.versioning.versioning` (T084).
