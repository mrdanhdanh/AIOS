# TASK-025 — Model Router

## Objective
Select model by policy, capability, cost, and health. Deterministic-first routing with fallback support.

## Deliverables
- `aios/model_router/__init__.py`
- `aios/model_router/contracts.py` — ModelRequirement, ModelCandidate, ModelSelection
- `aios/model_router/router.py` — model selection logic
- `aios/model_router/health.py` — model health tracking
- `aios/model_router/tests/` — tests

## Acceptance Criteria
- AC-025-01: Model selected by policy+capability+cost+health
- AC-025-02: Deterministic routing for known cases
- AC-025-03: No LLM needed for normal routing
- AC-025-04..06: Rejection/policy/cost enforcement
- AC-025-07..09: Context window, fallback, policy bypass prevention
- AC-025-10: No eligible model → fail-closed
- AC-025-11: Selection has explanation and provenance
- AC-025-12: Not a God Object
- AC-025-13: Agent cannot access Provider/Model directly
- AC-025-14..17: Tests, INV-013, observability, offline

## Dependencies
- TASK-024 (Context Optimizer)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
