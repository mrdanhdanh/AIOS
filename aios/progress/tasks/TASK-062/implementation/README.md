# TASK-062 — Implementation

## Modules
- `contracts.py` — `ScheduleEntry` (goal_id, trigger, cron_expr, event_filter, manual_token, autonomy_level_required, enabled, next_fire) and `TriggerType` (CRON/EVENT/MANUAL).
- `scheduler.py` — `Scheduler` (durable registry, trigger engine: `evaluate_cron`/`evaluate_event`/`evaluate_manual`, activation policy `check_activation_policy`, fail-closed `activate` with `_trigger_satisfied`, audit trail) and `SchedulerGate` (thin wrapper delegating to `Scheduler.activate`).

## Design notes
- Scheduler is a capability on the Runtime — no second autonomous control plane.
- Activation always re-validates the trigger fail-closed, then the activation policy, then the Governor decision.
- Registry is a plain dict store (deterministic) designed to be persisted for T066 Durable Execution.
