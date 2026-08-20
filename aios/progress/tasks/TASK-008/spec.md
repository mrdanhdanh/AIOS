# TASK-008 — Workflow Definition + Compiler

## Objective
Make Workflow a first-class declarative contract of AIOS, fully independent of any execution engine.

## Scope
WorkflowDefinition YAML contract (name/version/description/nodes/edges/retries/timeout/resources/permissions), node/edge contracts, validation pipeline fail-closed, compiler abstraction (Mock + LangGraph with lazy langgraph import), deterministic simulation with llm_calls=0 tool_calls=0, CLI `aiagent run --simulate` + `aiagent workflow validate`, contract versioning via `WORKFLOW_CONTRACT >=1.0.0,<2.0.0`.

## Deliverables
- `aios/runtime/workflow/{contracts,definition,validation,compiler,simulation,__init__}.py`
- `aios/cli/workflow_cli.py`
- `aios/runtime/tests/{test_workflow,test_workflow_architecture}.py`
- governance artifacts under `aios/progress/tasks/TASK-008/`

## Acceptance Criteria
- AC-008-01 Declarative contract round-trips.
- AC-008-02 Every invalid form REJECTs with WorkflowError.
- AC-008-03 Same definition compiles via Mock + LangGraph.
- AC-008-04 Simulation success has llm_calls=0 tool_calls=0 deterministic topo.
- AC-008-05 No module-load langgraph import.
- AC-008-06 Contract versioning >=1.0.0,<2.0.0.
- AC-008-07 Fail-closed: invalid → FAIL/REJECT with error, no silent fallback.

## Dependencies
- TASK-003 (DONE)

## Governance references
- Rule 3/4 via workflow package + architecture tests.
