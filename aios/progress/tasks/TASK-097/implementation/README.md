# TASK-097 Implementation

Permission + Human Approval + Apply + Re-test + Rollback + Certification lives in
`aios/remediation_apply/`:

- `aios/remediation_apply/apply.py` — `ApplyResult`, `ApplyOrchestrator`.
- `aios/remediation_apply/tests/test_apply.py` — 6 apply/rollback/certify tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.runtime.permission` (PermissionBroker, PermissionScope, Permission) — T070
- `aios.autonomy_governor` (AutonomyGovernor, AutonomyAction, AutonomyRisk, ApprovalRequest, ActionContext) — T054/T067
- `aios.harness.verification` (VerificationPipeline, Verdict) — T030/T032
- `aios.certification.certifier` (Certifier) + `aios.certification.contracts` (CertStatus) — T073
- `aios.observability.audit` (AuditService) — T069
- `aios.remediation_simulation` (SimulationResult, SimulationGate) — T096
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
