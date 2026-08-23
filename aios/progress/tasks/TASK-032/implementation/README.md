# TASK-032 Implementation — Evaluation Harness + Metrics

Implementation lives in `aios/harness/` (M6 Harness — Evaluation).

```
aios/harness/
  evaluation.py  # Evaluation harness (output/trajectory evaluation)
  evaluators.py  # Evaluator base + Deterministic/Semantic/LLM/Human/Composite + trajectory eval
  contracts.py   # EvaluationResult, Metric
  __init__.py    # re-exports
  tests/
    test_evaluation.py
    test_evaluators.py
```

Evaluates output/trajectory via evaluator suite. Supports deterministic, semantic, LLM, human and composite evaluators.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
