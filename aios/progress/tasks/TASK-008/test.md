# TASK-008 — Test

## How to run
```
python -m pytest aios/runtime/tests/test_workflow.py aios/runtime/tests/test_workflow_architecture.py -q
python -m pytest aios -q
```

## What is covered
- Valid YAML parsing + round-trip + from_file + content_hash determinism + to_artifact (AC-008-01/06)
- Every invalid branch: missing name/version, invalid SemVer, missing/duplicate node id, edge to unknown node, duplicate edge, self-loop, cycle, unsupported permission, invalid resource (cpu/memory), retries/timeout <0, engine/langgraph forbidden keys, invalid YAML (AC-008-02/07 fail-closed)
- Engine independence: MockCompiler + LangGraphCompiler compile same definition, both return CompiledWorkflow, topo_order deterministic via sorted Kahn (AC-008-03)
- Simulation: simulate_yaml success with llm_calls=0 tool_calls=0, deterministic, events present, file-based simulate, invalid returns success=False (AC-008-04)
- Contract versioning: check_workflow_contract 1.0.0/1.9.9 PASS, 0.9.0/2.0.0 REJECT (AC-008-06)
- CLI: validate (both `validate` and `workflow validate`), run --simulate success, run without --simulate → 2, missing file → 1/2, --json output (AC-008-07)
- Architecture: no top-level `import langgraph` in any workflow module; package imports without langgraph; LangGraphCompiler lazy flag; engine-tagged representation; no engine keys in to_dict (AC-008-05)

## Result
- `aios/runtime/tests/test_workflow.py` — 39 tests PASS
- `aios/runtime/tests/test_workflow_architecture.py` — 5 tests PASS
- Full suite `python -m pytest aios -q` — 514 passed, 0 failed
