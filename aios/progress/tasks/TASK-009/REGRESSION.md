# TASK-009 — Regression

## Dependency closure (TASK-003)
Tested via `python -m pytest aios -q` (full harness, 470 tests):

- `aios/core/*` — contracts, container, events, planner, healthcheck, version, config, metadata, logging — PASS (inherited from TASK-003)
- `aios/runtime/*` — context, audit, artifact, permission, policy, execution, scheduler, state, resource, memory, knowledge, providers — PASS (470 total)
- `aios/governance/*` — registry, dependency, lifecycle, evidence, gates, architecture — PASS
- `aios/capability/*` — capability, prompt, catalog, graph, contracts, kernel wiring — PASS (94 new)

## Command
```
python -m pytest aios -q
```
Result: `470 passed in ~2.2s`, 0 failures, 0 errors.

## Evidence
- Full harness includes dependency closure `{TASK-003}` transitively (TASK-009 depends on TASK-003 per PLAN).
- Layering invariant held: `aios/capability` does not import `aios.runtime` / `aios.agents` / `aios.orchestrator` (architecture test PASS).
- No regression in TASK-001..007 behavior; kernel singleton wiring preserved (memory/knowledge still singleton-tested).
