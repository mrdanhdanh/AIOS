# Implementation — TASK-067 Autonomy Safety 1.0

This folder is the mandatory `IMPLEMENTING` artifact. The real implementation
lives in the package below (per governance rule: real code under
`aios/<package>/`, `implementation/` is a pointer only).

## Real module
`aios/autonomy_safety/`
- `contracts.py` — `AutonomyContext`, `AutonomyLevel`, `AutonomyBudget`, `RiskClass`, `SafetyDecision`, `SafeStopSignal`.
- `registry.py` — `AutonomyLevelRegistry`, `LevelPolicy` (reject silent elevation; human approval for L3/L4).
- `boundary.py` — `check_boundary`, `evaluate_action`, `BoundaryResult`, `EvaluationResult` (delegate to Governor T054; ASK→BLOCK fail-closed).
- `safe_stop.py` — `SafeStopPolicy` (fail-closed SAFE_STOP; T068 kill-switch hook; T055/T061 integration).
- `tests/test_autonomy_safety.py` — full AC + Test Matrix coverage.

## Integration
- Governor (T054): boundary authority via `AutonomyGovernor.decide`.
- Recovery (T055): `SafeStopPolicy.recovery_strategy()` → `RecoveryStrategy.SAFE_STOP`.
- Stuck (T061): `SafeStopPolicy.from_stuck_signal()` triggers safe-stop from a `StuckSignal`.
- Kill Switch (T068): optional `kill_switch` hook consumes `SafeStopSignal`.
