# TASK-062 — Critique 1

## Missing spec sections
- ScheduleEntry model + TriggerType in `contracts.py`.
- Trigger Engine (cron/event/manual) + Activation Policy + Scheduler Gate in `scheduler.py`.

## Risks
- Trigger not re-validated at activation → unscheduled execution. Mitigation: `Scheduler.activate` re-checks `_trigger_satisfied` fail-closed before policy.
- Governor bypass. Mitigation: activation requires Governor decision (ALLOW) or fails closed (BLOCK).
- Non-durable schedule. Mitigation: registry is a plain dict store designed to be persisted (T066); deterministic next_fire derivation.

## Verdict
Implementable. Proceed.
