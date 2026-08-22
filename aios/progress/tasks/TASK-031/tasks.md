# TASK-031 — Breakdown

## Steps
1. Create `aios/harness/scenario.py` — ScenarioDefinition (scenario_id, name, steps, expected_outcome, failure_injections, deterministic, compute_hash), FailureInjection, SimulationRunner (run, get_results)
2. Implement deterministic hash for Golden Scenario versioning
3. Implement SimulationRunner: iterate steps, mark simulated=True, no real tool/filesystem calls
4. Create `aios/harness/tests/test_scenario.py` — 5 tests (create, deterministic hash, run, no side effects, history)
5. Run architecture guard — verify no Harness → Runtime internal implementation
6. Run full suite — 1739/1739 PASS (5 new), no regressions

## Dependencies
- TASK-030 Execution Verification

## Exit Criteria
- All AC-031-01..10 PASS, gate PASS, no regressions
