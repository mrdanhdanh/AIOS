# TASK-103 Implementation

Autonomy Constitution + Audit Trail lives in `aios/autonomy_constitution/`:

- `aios/autonomy_constitution/constitution.py` — `ConstitutionDecision`, `AuditEntry`, `AutonomyConstitution`, `AuditTrail`, `ConstitutionEngine`.
- `aios/autonomy_constitution/CONSTITUTION.md` — ADR (supreme autonomy law, R1-R4).
- `aios/autonomy_constitution/tests/test_constitution.py` — 6 constitution/audit tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.autonomy_safety` (AutonomyLevel) — T067
- `aios.autonomy_governor` (AutonomyAction, AutonomyDecision, AutonomyRisk) — T054
- `aios.trust_budget` (TrustBudget) — T102
- `aios.kill_switch` (KillSwitchController, HaltSignal, HaltScope, HaltSource) — T068
- `aios.verification_integrity` (IntegrityChecker, sha256) — T078
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
