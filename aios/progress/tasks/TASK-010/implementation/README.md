# TASK-010 Implementation — Decision Pipeline

Implementation lives in `aios/orchestrator/` (M2 Orchestration layer).

```
aios/orchestrator/
  __init__.py
  normalizer.py          # NormalizedRequest, Normalizer
  rule_engine.py         # RuleDecision, RuleEngine
  workflow_matcher.py    # WorkflowLibrary, WorkflowMatcher
  execution_plan.py      # ExecutionPlan, PlanNode, PlanEdge
  planner.py             # Planner, PlannerRequest/Response
  decision_pipeline.py   # DecisionPipeline, DecisionResult, DecisionEvidence
  tests/
    test_normalizer.py
    test_rule_engine.py
    test_workflow_matcher.py
    test_execution_plan.py
    test_planner.py
    test_decision_pipeline.py
    test_architecture.py
aios/governance/deterministic/pipeline.py  # enhanced + backward compat
```

See `../spec.md`, `../test.md`, `../evaluation.md`, `../REGRESSION.md` for
acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (601 PASS).
