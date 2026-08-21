# TASK-014 — Regression

## Dependency closure (M1 Runtime + TASK-010 + TASK-012 + TASK-013)

Tested via `python -m pytest aios -q` (full harness, 1014 tests):

- `aios/core/*` — contracts, container, events, planner, healthcheck, version, config, metadata, logging — PASS
- `aios/runtime/*` — context, audit, artifact, permission, policy, execution, scheduler, state, resource, memory, knowledge, workflow, capability_router — PASS (7 new)
- `aios/governance/*` — registry, dependency, lifecycle, evidence, gates, architecture (hardening + base), deterministic — PASS
- `aios/capability/*` — capability, prompt, catalog, graph, contracts, kernel wiring — PASS (health 5-state backward compat)
- `aios/agents/*` — orchestrator, spec_writer, critic, reviewer — PASS
- `aios/orchestrator/*` — normalizer, rule_engine, workflow_matcher, execution_plan, planner, decision_pipeline, goal_manager, task_queue, permission_broker, failure_recovery, architecture — PASS
- `aios/worker/*` — contract, lifecycle, registry, router, execution, workers, architecture, integration — PASS (161 tests)
- `aios/tool/*` — contracts, registry, adapters, router, policy_integration, architecture — PASS (156 new)

## Command
```
python -m pytest aios -q
```
Result: `1014 passed in ~3.8s`, 0 failures, 0 errors, 0 skipped.

Previous baseline before TASK-014: 851 passed. Delta: +163 (TASK-014 tool+router suite: 156 tool + 7 runtime).

## Evidence
- Full harness includes dependency closure `{M1, TASK-010, TASK-012, TASK-013}` transitively (TASK-014 depends on M1 Runtime + TASK-010/012 per spec).
- Tool Contract: 6 types, 5 health states, UNKNOWN fail-closed, version/compatibility.
- Tool Registry: dynamic Capability→Tool[] discovery, multi-tool, health/priority, thread-safe.
- 6 Adapters: offline mocks, no subprocess/network, standardized ToolResult.
- Capability Router: health/priority/policy, fail-closed, evidence, constraints, offline.
- Policy Integration: pre-check before selection, priority not override DENY, fallback only when allowed.
- Architecture: tool only core/stdlib, router at runtime, worker/agent not import tool, guard PASS.
- No regression in M1, TASK-010, TASK-012, TASK-013 suites; Tool+Capability is additive (3 new modules in aios/tool + 1 router in aios/runtime + kernel wiring + capability health extension).
