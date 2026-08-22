# TASK-097 — Permission + Human Approval + Apply + Re-test + Rollback + Certification

## Objective
Thực thi **Apply remediation** đã qua simulation gate (T096): xin Permission + Human
Approval (khi cần), Apply candidate, Re-test qua harness, Rollback nếu fail, và
Certify kết quả. TASK-097 là **apply/rollback orchestration, không phải detection**
(dựa trên Simulation T096 + Permission T070 + Governor T054 + Harness T030/T032 +
Certification T073).

## Scope
**In scope:** `aios/remediation_apply/` — ApplyResult, ApplyOrchestrator. Tích hợp
Simulation (T096) + Permission (T070) + Governor (T054) + Harness (T030/T032) +
Certification (T073).
**Out of scope:** detection/diagnosis; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/remediation_apply/apply.py` — permission + approval + apply + re-test + rollback + certify.
- `aios/remediation_apply/tests/test_apply.py` — 6 tests (Test Matrix).
- Tích hợp với Simulation (T096) + Permission (T070) + Governor (T054) + Harness + Certification (T073).

## Acceptance Criteria
- Mọi apply qua permission broker (T070).
- High-risk candidate cần human approval (T054/T067).
- Thiếu permission → không apply (fail-closed).
- Re-test FAIL → rollback (T074/T066).
- Kết quả cuối được certify (T073).
- Mọi bước có provenance (T001 Rule 5).
- Cùng candidate + policy → cùng apply result (deterministic).
- Tích hợp được với Simulation + Permission + Governor + Harness + Certification.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T096 (Simulation Gate) → T097 → T098.
- T070 (Permission), T054 (Governor), T073 (Certification), T030/T032 (Harness), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `remediation_apply` là `unknown`
  layer; chỉ import stdlib + `aios.runtime.permission` + `aios.autonomy_governor` + `aios.harness.verification` + `aios.certification` + `aios.remediation_simulation` + `aios.governance.evidence`.
