# TASK-008 — Evaluation

## Acceptance criteria results
| AC | Result | Evidence |
|----|--------|----------|
| AC-008-01 Declarative contract | PASS | test_valid_yaml_parses_and_roundtrips |
| AC-008-02 Validation | PASS | missing_name/version, invalid SemVer, duplicate node/edge, edge to unknown, self-loop, cycle, unsupported permission, invalid resource, retries/timeout, engine key, invalid YAML |
| AC-008-03 Engine independence | PASS | test_both_compilers_same_definition, mock + langgraph each compile same definition |
| AC-008-04 Simulation | PASS | test_simulate_yaml_success: llm_calls=0 tool_calls=0, deterministic, events, topo_order |
| AC-008-05 Compiler isolation | PASS | architecture: no top-level import langgraph, lazy compile only |
| AC-008-06 Contract versioning | PASS | content_hash deterministic, to_artifact version, check_workflow_contract boundaries |
| AC-008-07 Fail-closed | PASS | invalid → REJECT/FAIL, compiler rejects invalid, CLI exit 1/2 |

## Regression
- Dependency closure: TASK-003 (SemVer/contracts) — green.
- Full suite 514 passed.
- CLI: `aiagent run workflow.yaml --simulate` PASS with llm_calls=0 tool_calls=0; `aiagent workflow validate` + `aiagent validate` PASS; missing --simulate → 2.
