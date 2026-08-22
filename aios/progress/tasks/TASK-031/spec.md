# TASK-031 — Test Harness + Scenario + Simulation

## Objective
Build the Test Harness layer that runs declarative Scenario Definitions in deterministic Simulation Mode without real side effects, reusing Harness Kernel (TASK-029) and Verification/Evidence (TASK-030). Supports Golden Scenarios and failure injection for Retry/Fallback/Recovery/Policy verification.

## Scope
### In scope
- Test Harness orchestration: Load Scenario → Prepare Environment → Execute → Capture Trace → Verify → Evidence → Report
- Scenario Definition contract (id, version, input, environment, expectations, verification, faults, metadata)
- Simulation Mode via Fake Runtime/Fake Tool (no real tool calls, no filesystem writes outside sandbox)
- Golden Scenario management (deterministic, versioned, regression baseline)
- Failure injection (model timeout, tool failure, resource exhausted)
- Integration with Harness Kernel and Verification Pipeline
- CLI: `aiagent harness test`, `--scenario`, `--simulate`

### Out of scope
- Replacing pytest/vitest (Harness orchestrates, runners execute)
- Evaluation Harness (TASK-032)
- Benchmark/Regression Gate (TASK-033)
- Distributed execution (M7)

## Deliverables
- `aios/harness/scenario.py` — ScenarioDefinition, FailureInjection, SimulationRunner
- `aios/harness/tests/test_scenario.py` — scenario and simulation tests
- `aios/harness/tests/test_kernel.py` — kernel reuse tests
- `aios/harness/tests/test_verification.py` — verification integration tests

## Acceptance Criteria
- AC-031-01: Valid scenario parsed/validated; invalid schema rejected fail-closed
- AC-031-02: Golden deterministic scenario gives same outcome and logical trace on repeated runs
- AC-031-03: Simulation creates no real side effects (no real tool calls, no real filesystem writes)
- AC-031-04: Deterministic scenarios run offline without LLM/provider
- AC-031-05: Every Test Run goes through TASK-030 Verification and creates Evidence Package
- AC-031-06: Failure injection (model timeout/tool failure/resource exhausted) triggers correct failure path
- AC-031-07: Golden Scenario failure → Test Harness returns FAIL (not auto PASS)
- AC-031-08: Insufficient evidence → INCONCLUSIVE/UNKNOWN, not promoted to PASS
- AC-031-09: No new Runtime implementation inside Harness; Harness calls Runtime via contract/API only
- AC-031-10: Full regression M0–M5 PASS

## Dependencies
- TASK-030 — Execution Verification + Evidence + Replay

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-017 Harness Isolation, INV-018 Evidence First enforced.
