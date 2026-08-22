# TASK-063 — Regression

## Scope
T063 changes only governance docs + a re-export module (`baseline.py`). No runtime
behavior, no layer-order change, no new imports in `aios/agents/` or `aios/runtime/`.

## Regression check
- `python -m pytest aios/governance/architecture -q` → **124 passed**.
- No existing test modified or removed; `test_baseline.py` added only.
- `baseline.py` imports `guard.py` (downward, within `governance/architecture`) —
  respects architecture guard; `governance` is `unknown` infra, no ARCH-004 risk.

## Invariants preserved
- `LAYER_ORDER` and `ARCH_RULES` remain defined solely in `guard.py`.
- `ARCHITECTURE_VERSION = "1.0"` is the only new frozen marker.
- Fail-closed + deterministic properties of the guard unchanged.

## Result
REGRESSION: PASS (no regression, no invariant violation).
