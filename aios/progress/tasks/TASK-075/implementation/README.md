# TASK-075 — Implementation

This directory is a pointer to the real implementation (per task-folder standard:
`implementation/` holds a README pointing to the real module; no source is duplicated here).

## Real modules
- `aios/model_router/contracts.py` — `ModelRoute` dataclass (independence contract).
- `aios/model_router/router.py` — `ModelRouter.route()` (policy-driven `ModelRoute`),
  `ModelRouter.attempt_fallback()` (T055 recovery-driven fallback), `_eligible_chain()`.
- `aios/model_router/deterministic_route.py` — `DeterministicRouter` (Rule 4: LLM only on
  INSUFFICIENT; returns `llm_call_count`).
- `aios/cost_meter/__init__.py`, `aios/cost_meter/cost_meter.py` — `CostMeter`,
  `CostExceeded`, `CostRecord` (per-step/goal metering + fail-closed budget guard).
- `aios/cost_meter/perf_budget.py` — `PerformanceBudget`, `SLO`, `SLOViolation`
  (T069 SLO stand-in; latency/throughput within budget).

## Integration points
- `aios.governance.deterministic.DeterministicControlPath` (T001 Rule 4).
- `aios.autonomous_recovery.{FailureClassifier, RecoveryController, RecoveryStrategy}` (T055).
- `aios/autonomy_safety` / `aios/kill_switch` — absent; `CostExceeded` is emitted instead.

## Tests
- `aios/model_router/tests/test_t075.py`
- `aios/cost_meter/tests/test_cost_meter.py`

Run: `python -m pytest aios/model_router aios/cost_meter -q`
