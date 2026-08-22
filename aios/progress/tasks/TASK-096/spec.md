# TASK-096 — Simulation + Meta-Verification Gate

## Objective
Trước khi apply remediation, mô phỏng (simulate) candidate trong môi trường an toàn
và chạy meta-verification (T091) để xác nhận candidate thực sự khắc phục mà không
gây hại. TASK-096 là **simulation gate, không phải apply** (dựa trên Candidate T095
+ Meta T091 + Harness T030/T032).

## Scope
**In scope:** `aios/remediation_simulation/` — Sandbox, SimulationEngine,
SimulationGateEngine, SimulationResult. Tích hợp Candidate (T095) + Meta (T091) +
Harness (T030/T032).
**Out of scope:** apply/rollback; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/remediation_simulation/simulation.py` — simulate + meta-verify + gate.
- `aios/remediation_simulation/tests/test_simulation.py` — 7 tests (Test Matrix).
- Tích hợp với Candidate (T095) + Meta (T091) + Harness (T030/T032).

## Acceptance Criteria
- Candidate được simulate trong sandbox an toàn.
- Outcome quan sát qua harness (T030/T032).
- Simulate FAIL → REJECT (fail-closed).
- Meta-verify FAIL → REJECT (T091).
- Mọi simulation có provenance (T001 Rule 5).
- Cùng candidate + sandbox → cùng outcome (deterministic).
- Tích hợp được với Candidate + Meta + Harness.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T095 (Candidate Generation) → T096 → T097.
- T091 (Meta-Harness), T030/T032 (Harness), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `remediation_simulation` là `unknown`
  layer; chỉ import stdlib + `aios.harness.verification` + `aios.meta_harness` + `aios.remediation_candidate` + `aios.governance.evidence`.
