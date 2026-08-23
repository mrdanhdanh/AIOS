# TASK-033 Implementation — Benchmark + Regression Gate

Implementation lives in `aios/harness/` (M6 Harness — Benchmark).

```
aios/harness/
  benchmark.py  # Benchmark runner, comparison (quality/cost/latency/token/failure/policy)
  contracts.py  # BenchmarkResult, RegressionGate
  evaluation.py # GateEvaluator (PASS/WARNING/FAIL/INCONCLUSIVE)
  __init__.py   # re-exports
  tests/
    test_benchmark.py
    test_regression_gate.py
```

Compares versions by quality/cost/latency/token/failure/policy. `GateEvaluator` returns `PASS/WARNING/FAIL/INCONCLUSIVE` (fail-closed, `UNKNOWN` never promoted).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
