# TASK-102 — Trust Budget + Autonomy Levels + SAFE-STOP

## Objective
Thiết lập **Trust Budget + Autonomy Levels + SAFE-STOP** — giới hạn trust budget cho autonomous action: mỗi hành động tiêu trust, cạn → SAFE-STOP; kết hợp autonomy levels (T067) và kill switch (T068). TASK-102 là **trust accounting + safe-stop, không phải governor mới**.

## Scope
**In scope:** `aios/trust_budget/` — TrustBudget, TrustBudgetEngine. Tích hợp Autonomy Safety (T067) + Kill Switch (T068) + Governor (T054) + Evidence (T001).
**Out of scope:** xây governor mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/trust_budget/budget.py` — trust budget engine (6 tests).
- `aios/trust_budget/tests/test_budget.py` — 6 tests (Test Matrix).
- Tích hợp Autonomy Safety (T067) + Kill Switch (T068) + Governor (T054) + Evidence (T001).

## Acceptance Criteria
- Mỗi goal/loop có trust budget được theo dõi.
- Budget cạn → SAFE-STOP (fail-closed, T068).
- Action vượt remaining budget → BLOCK (T054/T067).
- Budget coupling với autonomy level (T067).
- Mọi thay đổi budget có provenance (T001 Rule 5).
- Cùng action + budget → cùng consume result (deterministic).
- Tích hợp được với Autonomy + Kill Switch + Harness Trust + Governor.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T101 (Continuous Certification) → T102 → T103.
- T067 (Autonomy Safety), T068 (Kill Switch), T054 (Governor), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `trust_budget` là `unknown` layer; chỉ import stdlib + `aios.autonomy_safety` + `aios.autonomy_governor` + `aios.kill_switch` + `aios.governance.evidence`.
