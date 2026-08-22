# TASK-051 Implementation

## Modules
- `contracts.py` — `AutonomousPlan`, `PlanTask`, `PlanStatus`, `ReplanTrigger`, `ReplanSafety`.
- `validation.py` — `PlanValidator` with 8 deterministic validation stages; `PlanValidationResult`.
- `planner.py` — `AutonomousPlanner` with deterministic-first strategy ladder, `PlannerContext`, `ReplanDecision`, `classify_replan_safety`, `replan`.

## Design notes
- Planner owns planning only; delegates policy/permission/resource/execution to Runtime/Governor.
- LLM is never the default path; `llm_call_count` is tracked for governance.
- Re-plan produces a new immutable version; the prior plan is marked SUPERSEDED (no overwrite).
- Validation is context-aware: capabilities/permissions/budget come from `PlannerContext`.
