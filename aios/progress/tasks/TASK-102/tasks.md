# Task Breakdown — TASK-102

- [x] TrustScope enum (goal | loop).
- [x] TrustBudget dataclass (scope, total, consumed, remaining, autonomy_level, safe_stop_on_empty, evidence_ref).
- [x] TrustBudgetEngine.policy_for_level (T067 coupling).
- [x] TrustBudgetEngine.create_budget (versioned, provenance).
- [x] TrustBudgetEngine._cost (risk-based consume).
- [x] TrustBudgetEngine.consume (fail-closed: exceeds -> BLOCK; empty -> SAFE-STOP).
- [x] TrustBudgetEngine._safe_stop (T068 halt).
- [x] TrustBudgetEngine.is_safe_stopped (T068 query).
- [x] TrustBudgetEngine._record_evidence (T001 provenance).
- [x] TrustBudgetEngine.provenance_complete / result_hash.
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Autonomy Safety + Kill Switch + Governor + Evidence (import-level).
