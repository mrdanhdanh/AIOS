# Tasks — TASK-075

- [x] Add `ModelRoute` dataclass to `aios/model_router/contracts.py` (intent, selected_provider, fallback_providers, cost_estimate, latency_budget, evidence_ref, policy, provenance).
- [x] Refactor `ModelRouter.select` to share `_eligible_chain`; add `route()` (policy-driven `ModelRoute`) and `attempt_fallback()` (T055 integration).
- [x] Add `aios/model_router/deterministic_route.py` with `DeterministicRouter` (Rule 4 — LLM only on INSUFFICIENT, returns `llm_call_count`).
- [x] Create `aios/cost_meter/` package: `CostMeter`, `CostExceeded`, `CostRecord`, `PerformanceBudget`, `SLO`, `SLOViolation`.
- [x] Export new symbols from `aios/model_router/__init__.py` and `aios/cost_meter/__init__.py`.
- [x] Write tests in `aios/model_router/tests/test_t075.py` and `aios/cost_meter/tests/test_cost_meter.py` covering every AC + Test Matrix row.
- [x] Run `python -m pytest aios/model_router aios/cost_meter -q` and make them PASS.
