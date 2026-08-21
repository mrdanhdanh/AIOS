# TASK-014 — Breakdown

- [x] **14.1** Create `aios/tool/` package — `__init__.py`, `contracts.py` (ToolContract, ToolHealth, ToolType, ToolResult, CapabilityRequest/Resolution, ResolutionStatus/Reason, ToolError, version/compatibility).
- [x] **14.2** Implement `aios/tool/registry.py` — ToolRegistry (register/unregister, lookup by id/capability, enable/disable, health/priority, version check, dynamic Capability→Tool[] mapping, thread-safe RLock).
- [x] **14.3** Implement `aios/tool/adapters.py` — 6 adapters (Python/Docker/REST/MCP/Shell/Git) + BaseToolAdapter, each declares capabilities, offline mock, standardized ToolResult.
- [x] **14.4** Implement `aios/runtime/capability_router.py` — CapabilityRouter (resolve CapabilityRequest→CapabilityResolution, health filter, priority selection, Policy pre-check, fail-closed UNRESOLVED, evidence).
- [x] **14.5** Update `aios/capability/capability.py` — extend health to 5-state (UNKNOWN/HEALTHY/DEGRADED/UNHEALTHY/DISABLED) with backward compat.
- [x] **14.6** Update `aios/runtime/kernel.py` — wire ToolRegistry + CapabilityRouter into Container, health snapshot.
- [x] **14.7** Create `aios/tool/tests/` — contract/registry/adapter/router/policy/offline/architecture tests (≥50 tests).
- [x] **14.8** Run `python -m pytest aios -q` — verify 690+ tests PASS, no architecture violations.
- [x] **14.9** Write `test.md` + `evaluation.md` + `REGRESSION.md` with evidence.
- [x] **14.10** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-014 DONE.
