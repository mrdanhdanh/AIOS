# TASK-090 — Harness Coverage + Readiness

## Objective
Đo lường và nâng **Harness Coverage + Readiness** — đảm bảo harness (T030/T032/T078/
T079/T089) bao phủ đủ bề mặt hệ thống và sẵn sàng (readiness) để chứng nhận build.
TASK-090 là **coverage/readiness metric, không phải harness mới** (dựa trên Harness
+ Certification T073).

## Scope
**In scope:** `aios/harness_coverage/` — CoverageMap, CoverageChecker, CoverageReport,
Readiness. Tích hợp Harness (T030/T032/T089) + Certification (T073).
**Out of scope:** harness mới; provider/filesystem adapters.

## Deliverables
- `aios/harness_coverage/coverage.py` — coverage map + readiness gate + gap report.
- `aios/harness_coverage/tests/test_coverage.py` — 7 tests (Test Matrix).
- Tích hợp với Harness (T030/T032/T089) + Certification (T073).

## Acceptance Criteria
- Coverage map ánh xạ đủ bề mặt hệ thống.
- Coverage dưới ngưỡng → NOT_READY (fail-closed).
- Gap được report (không giấu).
- Mọi readiness check có provenance (T001 Rule 5).
- Cùng system + harness → cùng coverage (deterministic).
- Tích hợp được với Harness + Certification.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T089 (Behavioral Conformance) → T090 → T091.
- T030/T032 (Harness), T073 (Certification), T089 (Behavioral).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `harness_coverage` là `unknown`
  layer; chỉ import stdlib + `aios.harness` + `aios.certification` + `aios.behavioral`.
