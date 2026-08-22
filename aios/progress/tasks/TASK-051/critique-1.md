# TASK-051 — Critique 1

## Missing spec sections
- Spec does not yet enumerate the exact `AutonomousPlan` field list — addressed in `contracts.py`.
- Re-plan safety matrix needs explicit mapping from trigger → safety level — added in `planner.classify_replan_safety`.

## Risks
- LLM fallback could become the default if deterministic ladder is too weak. Mitigation: `llm_call_count` tracked and asserted 0 in deterministic tests.
- Validation could be bypassed before execution. Mitigation: `plan()` sets status REJECTED when invalid; loop/executor must check status.

## Verdict
Spec is implementable. Proceed to implementation.
