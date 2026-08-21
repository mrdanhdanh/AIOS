# TASK-012 — Regression

## Dependency closure (TASK-010, M1 Runtime)

Tested via `python -m pytest aios -q` (full harness, 690 tests):

- `aios/core/*` — contracts, container, events, planner, healthcheck, version, config, metadata, logging — PASS
- `aios/runtime/*` — context, audit, artifact, permission, policy, execution, scheduler, state, resource, memory, knowledge, workflow — PASS
- `aios/governance/*` — registry, dependency, lifecycle, evidence, gates, architecture (hardening + base), deterministic — PASS
- `aios/capability/*` — capability, prompt, catalog, graph, contracts, kernel wiring — PASS
- `aios/agents/*` — orchestrator, spec_writer, critic, reviewer — PASS
- `aios/orchestrator/*` — normalizer, rule_engine, workflow_matcher, execution_plan, planner, decision_pipeline, goal_manager, task_queue, permission_broker, failure_recovery, architecture — PASS (89 new + 57 inherited)

## Command
```
python -m pytest aios -q
```
Result: `690 passed in ~2.6s`, 0 failures, 0 errors, 0 skipped.

Previous baseline before TASK-012: 601 passed. Delta: +89 (TASK-012 orchestration suite).

## Evidence
- Full harness includes dependency closure `{TASK-010, M1}` transitively (TASK-012 depends on TASK-010 per spec).
- Goal persistence: file-based JSON roundtrip verified (save/load with restart simulation).
- TaskQueue: dependency-aware, priority not override, explicit unblock, no cron.
- Permission Broker: delegates to PolicyEngine, DENY→BLOCKED, ASK→human approval.
- Failure Recovery: bounded retry, policy-gated fallback, no infinite retry.
- No regression in M1 or TASK-010 suites; orchestration is additive (4 new modules + __init__ update).
