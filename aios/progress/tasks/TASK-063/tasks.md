# TASK-063 — Breakdown

## Subtasks
1. **ADR** — write `docs/adr/ADR-ARCH-1.0.md` freezing the 1.0 baseline
   (5 layers + ARCH-001..004 + freeze-safety principles). → `DONE`
2. **Baseline module** — create `aios/governance/architecture/baseline.py` with
   `ARCHITECTURE_VERSION="1.0"` and `frozen_layer_contract()` re-exporting
   `guard.py` constants (single source of truth). → `DONE`
3. **Guard verification** — confirm `guard.py` implements ARCH-001..004
   fail-closed + deterministic (pure AST, no network/clock/random). → `DONE`
4. **Tests** — add `aios/governance/architecture/tests/test_baseline.py` covering
   the full T063 §7 matrix + baseline codification. → `DONE`
5. **Artifacts** — produce the 9 progress artifacts (this file + spec/critiques/
   review/implementation/test/evaluation/regression). → `DONE`

## Verification
- `python -m pytest aios/governance/architecture -q` → all PASS (124).
