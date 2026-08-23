# TASK-031 Implementation — Test Harness + Scenario + Simulation

Implementation lives in `aios/harness/` (M6 Harness — Test Harness).

```
aios/harness/
  test_harness.py  # TestHarness, FakeRuntime, FakeTool, GoldenScenario, run_harness_test
  scenario.py      # Scenario definitions, deterministic simulation
  contracts.py     # Scenario, TestResult
  __init__.py      # re-exports
  tests/
    test_harness_gaps.py
    test_scenario.py
```

Runs deterministic scenarios and simulations. `FakeRuntime`/`FakeTool` enable offline testing without LLM or network.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
