# TASK-061 — Critique 1

## Missing spec sections
- StuckSignal model + StuckPolicy in `contracts.py`.
- Detector tiers (oscillation/plateau/resource-burn) in `detector.py`.

## Risks
- Oscillation guessed from one point. Mitigation: detection uses repeated trajectory hash over a window.
- Low-confidence false positive → auto-continue. Mitigation: `StuckPolicy.resolve` escalates when confidence < threshold or evidence missing (fail-closed).

## Verdict
Implementable. Proceed.
