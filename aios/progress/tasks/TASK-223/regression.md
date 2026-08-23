# Regression — TASK-223

Scope: full AIOS suite + task gate.

- `python -m pytest aios -q` must remain green. The new `test_website.py` adds
  two passing tests (AIOS build + Node behavior harness) and modifies no existing
  modules. `aios/tool/website/` and `aios/governance/runtime_utilization/` are
  additive.
- `python aios/governance/cli/gate_check.py --task TASK-223`:
  - lifecycle: all artifacts present
  - architecture: no violations
  - **runtime_utilization: PASS** (AIOS genuinely exercised — the TASK-222 loophole is closed)
  - ci/registry/dependency/evidence/test_evaluate/regression: PASS

**Result: NO REGRESSION.** The deliverable is additive and isolated under
`aios/progress/tasks/TASK-223/`. The new gate only *adds* a fail-closed check
for `Demonstrates-AIOS` tasks; existing tasks are unaffected (marker absent).
