# TASK-029 Implementation — Harness Kernel + Contract + Registry + Run

Implementation lives in `aios/harness/` (M6 Harness — Kernel).

```
aios/harness/
  contracts.py  # HarnessSpec, HarnessRun, RunStatus, RunResult, Assertion
  kernel.py     # HarnessKernel (create_run, execute, get_run, list_runs, register_step)
  registry.py   # HarnessRegistry (AC-029-02)
  __init__.py   # re-exports (HarnessContext, HarnessEvent, HarnessArtifact, HarnessReport)
  tests/
    test_kernel.py
    test_verification.py
```

Lifecycle: `CREATED → PREPARING → VALIDATING → RUNNING → VERIFYING → COMPLETED` (failure: `RUNNING → FAILED → DIAGNOSED`). Deterministic, fail-closed, no direct Runtime implementation access (INV-017).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
