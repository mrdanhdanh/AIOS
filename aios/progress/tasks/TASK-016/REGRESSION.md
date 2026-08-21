# TASK-016 — Regression (REGRESSION.md)

## Dependency closure
`{ TASK-010, TASK-012, TASK-013, TASK-014, TASK-015, M0/M1 }` — all DONE.

## Full suite
```
python -m pytest aios -q
1257 passed in 5.55s
```

## Gate behavior (fail-closed)
- Any ERROR violation -> FAIL.
- Any UNKNOWN (scan/rule/graph error) -> FAIL, never promoted to PASS.
- Exception during evaluation -> FAIL (ARCH-004 / ARCH-D-001 fallback).
- WARNING/INFO architecture violations -> FAIL (strict gate).

## Integration with prior tasks
- T011 hardening (`guard.py`) extended with skill layer + delegation to
  scanner/rules (step 16.7). Backward-compatible `ArchitectureGuard` re-exported.
- No increase in architecture violations across M2 modules.

## CI
Architecture tests run as part of `pytest aios`; gate must PASS for release.
