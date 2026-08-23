# TASK-022 Implementation — Orchestrator v2

Implementation lives in `aios/orchestrator/v2/` (M4 Platform Edition — Orchestrator v2).

```
aios/orchestrator/v2/
  supervisor.py  # ExecutionSupervisor (execution lifecycle, policy-checked)
  evaluator.py   # EvaluationCollector (collects execution evaluations)
  advisor.py     # ImprovementAdvisor (suggests improvements, no bypass)
  reporter.py    # GoalReporter (goal progress reporting)
  __init__.py    # re-exports
  tests/
    test_supervisor.py
    test_evaluator.py
    test_advisor.py
    test_reporter.py
```

Orchestrator v2 remains **not a God Object** — improvement only suggests, never bypasses Policy. Evaluation and goal reporting are separate concerns.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
