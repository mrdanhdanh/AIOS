# TASK-075 — Regression

## Dependency closure
- T001 (deterministic Rule 4) — used via `aios.governance.deterministic`. ✔
- T055 (recovery/fallback) — used via `aios.autonomous_recovery`. ✔
- T074 (Upgrade & Migration 1.0) — predecessor milestone. ✔
- T069 (reliability SLO) — absent; SLO implemented locally in `aios/cost_meter.perf_budget`. ✔

## Regression result
- Re-ran the tests of the affected packages: `python -m pytest aios/model_router aios/cost_meter -q`.
- Existing `aios/model_router/tests/test_router.py` and `test_fallback.py` remain green
  (the `select` refactor preserves exact prior behavior via shared `_eligible_chain`).
- No architecture-guard violations: `model_router`/`cost_meter` are `unknown` layer; imports
  are limited to `governance.deterministic`, `autonomous_recovery`, and intra-package modules.

## Status
- REGRESSION gate: PASS.
