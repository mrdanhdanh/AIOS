# TASK-011 — Regression

## Dependency closure (TASK-005, TASK-009 → TASK-002..009)

Tested via `python -m pytest aios -q` (full harness, 544 tests):

- `aios/core/*` — contracts, container, events, planner, healthcheck, version, config, metadata, logging — PASS
- `aios/runtime/*` — context, audit, artifact, permission, policy, execution, scheduler, state, resource, memory, knowledge, workflow (definition/validation/compiler/simulation/contracts/CLI) — PASS
- `aios/governance/*` — registry, dependency, lifecycle, evidence, gates, architecture (hardening + base) — PASS (30 new hardening tests included)
- `aios/capability/*` — capability, prompt, catalog, graph, contracts, kernel wiring — PASS
- `aios/agents/*` — orchestrator, spec_writer, critic, reviewer — PASS

## Command
```
python -m pytest aios -q
```
Result: `544 passed in ~2.3s`, 0 failures, 0 errors, 0 skipped.

Previous baseline before TASK-011: 514 passed. Delta: +30 (TASK-011 hardening suite).

## Evidence
- Full harness includes dependency closure `{TASK-002..009}` transitively (TASK-011 depends on TASK-005 and TASK-009 per PLAN).
- Layering invariant held: agent→runtime/capability/tool now correctly FAILS (hardened), capability→runtime FAILS, orchestrator→runtime PASS, runtime→capability PASS.
- `classify_module` dot-aware (`replace(".", "/")`) so `aios.runtime.providers` correctly maps to `tool`.
- Policy negative E2E: unprivileged subject on `workflow:forbidden` → DENY, execution not started, evidence via PolicyDecision.
- No regression in existing suites; guard scan over `aios/agents` clean post-hardening.
