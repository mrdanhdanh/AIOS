# TASK-025 — Breakdown

## Steps
1. Create `aios/model_router/contracts.py` — ModelRequirement, ModelCandidate, ModelSelection, RoutingDecision contracts
2. Create `aios/model_router/health.py` — ModelHealth (availability, failure rate, circuit state)
3. Create `aios/model_router/router.py` — ModelRouter pipeline: Extract Requirements → Policy Filter → Capability Filter → Availability Filter → Cost/Latency Filter → Rank → Select; FallbackResolver with policy check
4. Implement deterministic-first routing (no LLM for normal routing), explainability (rejected candidates with reason)
5. Implement fail-closed: NO_ELIGIBLE_MODEL / POLICY_DENIED / BUDGET_EXCEEDED, UNKNOWN not treated as compatible
6. Create `aios/model_router/tests/test_router.py` — 11 tests (policy, capability, cost, health, fallback, fail-closed, provenance)
7. Run architecture guard — verify no Agent → Provider direct access, no God Object
8. Run full suite — 1681/1681 PASS, no regressions

## Dependencies
- TASK-024 Context Optimizer

## Exit Criteria
- All AC-025-01..17 PASS, gate PASS, 1681 tests green
