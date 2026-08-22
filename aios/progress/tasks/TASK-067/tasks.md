# TASK-067 — Breakdown

- [x] Step 1 — Define `AutonomyContext`, `AutonomyLevel`, `AutonomyBudget`, `RiskClass`, `SafetyDecision`, `SafeStopSignal` in `contracts.py`.
- [x] Step 2 — Implement `AutonomyLevelRegistry` + `LevelPolicy` in `registry.py` (reject silent elevation; human approval for L3/L4).
- [x] Step 3 — Implement `check_boundary` + `evaluate_action` in `boundary.py` (delegate to Governor T054; ASK→BLOCK fail-closed).
- [x] Step 4 — Implement `SafeStopPolicy` in `safe_stop.py` (fail-closed signal; T068 hook; T055/T061 integration).
- [x] Step 5 — Export public API in `aios/autonomy_safety/__init__.py`.
- [x] Step 6 — Write pytest suite covering all ACs + Test Matrix rows in `aios/autonomy_safety/tests/`.
- [x] Step 7 — Run `python -m pytest aios/autonomy_safety -q` and make it green.
- [x] Step 8 — Produce lifecycle artifacts (spec/critique×2/tasks/review/implementation/test/evaluation/regression).
