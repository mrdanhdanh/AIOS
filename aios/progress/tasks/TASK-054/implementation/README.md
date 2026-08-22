# TASK-054 Implementation

## Modules
- `contracts.py` — `AutonomyPolicy`, `AutonomyMode`, `AutonomyAction`, `AutonomyRisk`, `AutonomyDecision`, `AutonomyBudget`, `ApprovalRequest`.
- `governor.py` — `AutonomyGovernor` with deterministic risk scoring, scope/budget checks, fail-closed `decide`, `request_approval`.

## Design notes
- Governor is the autonomy-specific gate; it consumes (not replaces) the Policy Engine / Permission Service.
- Risk is computed deterministically from 6 components; no LLM in the risk gate.
- Fail-closed: any unknown/uncertain condition → BLOCK. Unknown action → DESTRUCTIVE.
- Approval requests carry expiry and a `used` flag to prevent silent reuse.
