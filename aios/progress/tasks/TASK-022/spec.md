# TASK-022 — Orchestrator v2

## Objective
Upgrade Orchestrator to a control plane with execution supervision, evaluation collection, improvement proposals, and goal reporting — without becoming a God Object.

## Scope
### In scope
- Execution Supervisor (monitor lifecycle, detect failure/timeout)
- Evaluation Collector (gather evaluation data post-execution)
- Improvement Advisor (propose improvements from evidence)
- Goal Reporting (reflect true goal state)

### Out of scope
- Direct execution of workflows (existing orchestrator handles this)
- Model selection (TASK-025)
- Policy bypass (never allowed)

## Deliverables
- `aios/orchestrator/v2/__init__.py`
- `aios/orchestrator/v2/supervisor.py` — execution supervisor
- `aios/orchestrator/v2/evaluator.py` — evaluation collector
- `aios/orchestrator/v2/advisor.py` — improvement advisor
- `aios/orchestrator/v2/reporter.py` — goal reporter
- `aios/orchestrator/v2/tests/` — comprehensive tests

## Acceptance Criteria
- AC-022-01: Supervisor monitors execution lifecycle
- AC-022-02: Failure/timeout detected
- AC-022-03: Evaluation collected after execution
- AC-022-04: Evaluation has provenance
- AC-022-05: Improvement Advisor creates proposals from evidence
- AC-022-06: Proposals don't bypass Policy
- AC-022-07: Goal report reflects true state
- AC-022-08: Orchestrator doesn't become God Object
- AC-022-09: No second execution path created
- AC-022-10: M0–M3 regression PASS

## Dependencies
- TASK-021 (Observability)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
