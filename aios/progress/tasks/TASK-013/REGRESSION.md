# TASK-013 — Regression

## Dependency closure (TASK-010, TASK-012, M1 Runtime)

Tested via `python -m pytest aios -q` (full harness, 851 tests):

- `aios/core/*` — contracts, container, events, planner, healthcheck, version, config, metadata, logging — PASS
- `aios/runtime/*` — context, audit, artifact, permission, policy, execution, scheduler, state, resource, memory, knowledge, workflow — PASS
- `aios/governance/*` — registry, dependency, lifecycle, evidence, gates, architecture (hardening + base + worker layer), deterministic — PASS
- `aios/capability/*` — capability, prompt, catalog, graph, contracts, kernel wiring — PASS
- `aios/agents/*` — orchestrator, spec_writer, critic, reviewer — PASS
- `aios/orchestrator/*` — normalizer, rule_engine, workflow_matcher, execution_plan, planner, decision_pipeline, goal_manager, task_queue, permission_broker, failure_recovery, architecture — PASS (89 + 57 = 146)
- `aios/worker/*` — contract, lifecycle, registry, router, execution, workers, architecture, integration — PASS (161 new)

## Command
```
python -m pytest aios -q
```
Result: `851 passed in ~3.1s`, 0 failures, 0 errors, 0 skipped.

Previous baseline before TASK-013: 690 passed. Delta: +161 (TASK-013 worker suite).

## Architecture Guard

- `LAYER_ORDER` updated: `["agent", "orchestrator", "worker", "runtime", "capability", "tool"]`
- `LAYER_KEYWORDS` added: `worker`/`workers` → `worker`
- `ALLOWED_IMPORT_LAYERS` added: `worker: ["worker", "capability", "unknown"]`, `orchestrator` now allows `worker`
- `WORKER_FORBIDDEN` added: subprocess/os/provider/filesystem/runtime internals for worker layer
- `scan_source` extended for worker layer (ARCH-001..004)
- `python -m pytest aios/worker/tests/test_architecture.py -q` — 10 passed, 0 violations
- `python -m pytest aios/governance/architecture -q` — 6 passed, 0 violations
- Full harness architecture tests: all PASS

## Evidence
- Full harness includes dependency closure `{TASK-010, TASK-012, M1}` transitively (TASK-013 depends on TASK-010 + TASK-012 per spec).
- Worker Contract: 10 mandatory fields validated for all 4 workers.
- Capability-only access: no Worker→Tool/Runtime/Provider/filesystem/subprocess imports.
- Permission boundary: DENY→BLOCKED, cannot self-grant.
- Lifecycle: state machine controlled, worker reusable after task failure.
- Routing: capability-based, deterministic, health/policy-gated.
- No regression in M1, TASK-010 or TASK-012 suites; worker is additive (6 new modules + guard update).
