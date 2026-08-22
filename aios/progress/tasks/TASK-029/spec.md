# TASK-029 — Harness Kernel + Contract + Registry + Run

## Objective
Build the Harness Kernel as a shared subsystem with unified contracts and lifecycle for all Harness Runs: `Create → Prepare → Validate → Run → Verify → Complete/Fail → Diagnose`. Each run has traceable identity (`run_id`, harness, target, version, environment, started_at, status) enabling `Release → Harness Run → Execution Trace → Evaluation → Failure` provenance. Harness observes/calls Runtime via API/contract only — no direct Runtime implementation access (INV-017).

## Scope
### In scope
- Harness contracts: `HarnessSpec`, `HarnessRun`, `RunStatus`, `RunResult`, `Assertion`
- Harness lifecycle state machine: CREATED→PREPARING→VALIDATING→RUNNING→VERIFYING→COMPLETED, failure path RUNNING→FAILED→DIAGNOSED
- HarnessKernel: create_run, execute with step hooks, deterministic transitions, fail-closed on exception
- Run identity: unique `run_id` per run, no reuse
- Traceability: `get_run`/`list_runs` from `run_id`
- Isolation boundary: Harness does not import Runtime Service implementation
- Deterministic registry lookup and lifecycle (no LLM)

### Out of scope
- Execution Verification / Evidence Package / Replay (TASK-030)
- Test Harness + Scenario (TASK-031)
- Evaluation Harness (TASK-032)
- Benchmark/Regression/Doctor (TASK-033/034)
- Distributed harness (M7)

## Deliverables
- `aios/harness/__init__.py` — public API
- `aios/harness/contracts.py` — HarnessSpec, HarnessRun, RunStatus, RunResult, Assertion, HarnessError
- `aios/harness/kernel.py` — HarnessKernel (create_run, execute, get_run, list_runs, register_step)
- `aios/harness/tests/test_kernel.py` — contract, lifecycle, registry, failure, isolation tests
- `aios/harness/tests/test_verification.py` — shared verification pipeline tests (used by TASK-030)

## Acceptance Criteria
- AC-029-01: Harness and HarnessRun have stable, versionable, validatable schema
- AC-029-02: Registry duplicate `harness_id + version` rejected; lookup deterministic
- AC-029-03: Valid run follows CREATED→PREPARING→VALIDATING→RUNNING→VERIFYING→COMPLETED; invalid transition rejected
- AC-029-04: Exception in execution → FAILED (not COMPLETED), supports FAILED→DIAGNOSED
- AC-029-05: Each run creates unique `run_id`, no reuse
- AC-029-06: From `run_id` traceable to harness, target, version, environment, lifecycle events, final result
- AC-029-07: Architecture test fails if Harness imports Runtime Service implementation directly
- AC-029-08: Registry lookup and lifecycle transitions deterministic (no LLM)
- AC-029-09: Tests cover Unit, Contract, Lifecycle, Registry, Failure, Architecture, Integration, Regression
- AC-029-10: Design allows TASK-030 to reuse Kernel for Verification/Evidence/Replay without modifying Harness Core

## Dependencies
- TASK-028 — Parallel Scheduler

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-017 Harness Isolation enforced.
