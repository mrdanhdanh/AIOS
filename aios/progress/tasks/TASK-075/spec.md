# TASK-075 — Performance & Cost + Model Independence

## Objective
Add a perf/cost/independence layer to AIOS built on `aios/model_router` and a new
`aios/cost_meter` package: provider-agnostic policy-driven model routing, per-step/goal
cost metering with a fail-closed budget guard, performance-budget (SLO) checks, fallback
routing on provider failure (T055), and deterministic-first routing (Rule 4 / T001). No
provider lock-in.

## Scope
**In scope:** `ModelRoute` contract, `ModelRouter.route` / `attempt_fallback`,
`DeterministicRouter`, `CostMeter`, `PerformanceBudget`. Integration with
`aios.governance.deterministic` (T001), `aios.autonomous_recovery` (T055).
**Out of scope:** runtime rewrite, new provider adapters, `aios/reliability` (T069 — not
present; SLO implemented locally in `cost_meter.perf_budget`), `aios/autonomy_safety` /
`aios/kill_switch` (not present; `CostExceeded` emitted as the escalate/stop signal).

## Deliverables
- `aios/model_router/contracts.py` — `ModelRoute` dataclass (intent, selected_provider,
  fallback_providers, cost_estimate, latency_budget, evidence_ref, policy, provenance).
- `aios/model_router/router.py` — `route()`, `attempt_fallback()`, `_eligible_chain()`.
- `aios/model_router/deterministic_route.py` — `DeterministicRouter` (Rule 4).
- `aios/cost_meter/` (new) — `CostMeter`, `CostExceeded`, `CostRecord`, `PerformanceBudget`,
  `SLO`, `SLOViolation`.
- Tests covering every AC + Test Matrix row.

## Acceptance Criteria
- **AC1:** No hardcoded provider — selection via model router (policy-driven).
- **AC2:** Cost metered per-step/goal; exceeds budget → escalate/stop (fail-closed).
- **AC3:** Perf within SLO (latency/throughput).
- **AC4:** Provider down → fallback route (T055).
- **AC5:** LLM only fallback when deterministic INSUFFICIENT (Rule 4).
- **AC6:** Every route + cost has provenance evidence.
- **AC7:** Same intent + policy → same route (deterministic).
- **AC8:** Integrates with Model Router + Deterministic + Recovery.
- **AC9:** Prior milestone tests remain green; no invariant violations.

## Dependencies
- TASK-074 (Upgrade & Migration 1.0) — predecessor.
- T001 (deterministic Rule 4), T055 (recovery/fallback), T069 (reliability SLO, absent → local).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture guard: `model_router`/`cost_meter` are
  `unknown` layer; only downward/peer imports (no `agents/`, no provider/tool internals).
