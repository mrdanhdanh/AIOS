# TASK-011 — Test Report

## Suites

| Suite | File | Cases | Result |
|-------|------|-------|--------|
| m1 hardening | `aios/governance/architecture/tests/test_m1_hardening.py` | 30 | PASS |
| governance architecture | `aios/governance/architecture/tests/test_architecture.py` | 6 | PASS |
| capability architecture | `aios/capability/tests/test_capability_architecture.py` | 5 | PASS |
| core architecture | `aios/core/tests/test_architecture.py` | 8 | PASS |
| workflow | `aios/runtime/tests/test_workflow.py` | 39 | PASS |
| workflow architecture | `aios/runtime/tests/test_workflow_architecture.py` | 5 | PASS |
| full harness | `python -m pytest aios -q` | 544 | PASS |

## Coverage

- Guard hardening: `LAYER_KEYWORDS` (core/governance/harness/progress→unknown, kernel/workflow→runtime, providers→tool) + `ALLOWED_IMPORT_LAYERS` (agent→agent|orchestrator|unknown, capability→capability|unknown) asserted via `classify_module` and `scan_source` ARCH-001..004.
- Policy pre-check: DENY on missing permission (fail-closed), ALLOW after grant, negative E2E `POLICY DENY → execution_count 0`.
- Agent boundary: actual `aios/agents/*.py` and `aios/capability/*.py` scanned for forbidden imports.
- Workflow isolation: no module-load `langgraph` import, lazy compiler, mock topo.
- Kernel health: 17 keys + SINGLETON lifetimes for runtime+capability services.
- Offline: `simulate_definition` llm_calls=0 tool_calls=0, contracts via `check_runtime_contracts`/`check_capability_contracts`.
- `python -m pytest aios -q` — 544 passed, 0 failed.

## AC mapping

| AC | Cases | Result |
|----|-------|--------|
| AC-011-01 full M1 regression | full harness 544 | PASS |
| AC-011-02 architecture invariants | TestArchInvariants + TestLayerKeywords | PASS |
| AC-011-03 policy pre-check | TestPolicyPreCheck (3 tests) | PASS |
| AC-011-04 agent boundary | TestArchInvariants + TestAgentBoundary | PASS |
| AC-011-05 workflow isolation | TestWorkflowIsolation (3 tests) | PASS |
| AC-011-06 contracts | test_contract_versions_pass | PASS |
| AC-011-07 runtime composition | TestKernelHealth (2 tests) | PASS |
| AC-011-08 offline | test_simulation_offline_no_llm_no_tool | PASS |
| AC-011-09 evidence | audit/policy simulation events | PASS |
| AC-011-10 fail-closed | DENY→no execution, architecture violations→FAIL | PASS |
