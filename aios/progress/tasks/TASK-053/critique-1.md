# TASK-053 — Critique 1

## Missing spec sections
- Cycle status machine enumerated in `contracts.CycleStatus`.
- Stop-condition set mapped to deterministic checks in `loop.run`.

## Risks
- Cost/failure budgets must be loop-level accumulators, not per-cycle (per-cycle reset would never trigger MAX_COST). Mitigation: `self._total_cost` / `self._total_failures` added.
- Loop could become a second control plane. Mitigation: all side-effecting steps delegated to injected actor/observer/evaluator.

## Verdict
Implementable. Proceed.
