# TASK-025 Implementation — Model Router

Implementation lives in `aios/model_router/` (M5 Core Intelligence — Model Router).

```
aios/model_router/
  contracts.py          # ModelRequirement, ModelCandidate, ModelSelection, RoutingPolicy
  router.py             # ModelRouter (policy/capability/cost/health selection)
  deterministic_route.py# DeterministicRouter (deterministic-first, no LLM)
  fallback.py           # FallbackResolver (fallback chain)
  health.py             # ModelHealthTracker
  __init__.py           # re-exports
  tests/
    test_router.py
    test_fallback.py
    test_health.py
```

Selects model by policy, capability, cost and health. Deterministic routing first; fallback chain when primary unavailable.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
