# TASK-102 Implementation

Trust Budget + Autonomy Levels + SAFE-STOP lives in `aios/trust_budget/`:

- `aios/trust_budget/budget.py` — `TrustScope`, `TrustBudget`, `TrustBudgetEngine`.
- `aios/trust_budget/tests/test_budget.py` — 6 trust tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.autonomy_safety` (AutonomyLevel, AutonomyContext) — T067
- `aios.autonomy_governor` (AutonomyGovernor, AutonomyAction, ActionContext) — T054
- `aios.kill_switch` (KillSwitchController, HaltSignal, HaltScope, HaltSource) — T068
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
