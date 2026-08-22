# TASK-101 — Continuous Certification

## Objective
Thiết lập **Continuous Certification** — chứng nhận liên tục: mọi change (code/config/policy) chạy lại cert suite và chỉ deploy khi PASS. TASK-101 là **continuous cert gate, không phải certification mới** (dựa trên T073 + T087 + T090/T091 + T099).

## Scope
**In scope:** `aios/continuous_certification/` — ContinuousCertRun, ContinuousCertEngine. Tích hợp Certification (T073) + Conformance (T087) + Harness trust (T090/T091) + Loop (T099) + Scheduler (T062).
**Out of scope:** xây certification suite mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/continuous_certification/cert.py` — cert engine (6 tests).
- `aios/continuous_certification/tests/test_cert.py` — 6 tests (Test Matrix).
- Tích hợp Certification (T073) + Conformance (T087) + Harness trust (T090/T091) + Loop (T099).

## Acceptance Criteria
- Mọi change trigger certification (T062/T099).
- Toàn bộ cert suite chạy lại (T073/T087/T090/T091).
- Một gate FAIL → không deploy (fail-closed).
- Mọi cert run có provenance (T001 Rule 5).
- Cùng change + suite → cùng cert result (deterministic).
- Tích hợp được với Certification + Conformance + Harness trust + Loop.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T100 (Failure-Corpus) → T101 → T102.
- T073 (Certification), T087 (Conformance), T090/T091 (Coverage/Meta), T099 (Loop), T062 (Scheduler).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `continuous_certification` là `unknown` layer; chỉ import stdlib + `aios.certification` + `aios.conformance` + `aios.harness_coverage` + `aios.meta_harness` + `aios.readiness_trust` + `aios.governance.evidence`.
