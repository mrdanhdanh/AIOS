# TASK-014 — Implementation

Tool + Capability Layer implementation:

- `aios/tool/__init__.py` — re-exports (ToolContract, ToolRegistry, adapters, router contracts)
- `aios/tool/contracts.py` — ToolContract, ToolHealth (5-state), ToolType (6 types), ToolResult, CapabilityRequest/Resolution, ResolutionStatus/Reason, ToolCandidate, version/compatibility
- `aios/tool/registry.py` — ToolRegistry (register/unregister, lookup by id/capability, enable/disable, health/priority, version check, dynamic Capability→Tool[] mapping, thread-safe RLock)
- `aios/tool/adapters.py` — 6 offline mock adapters (Python/Docker/REST/MCP/Shell/Git) + BaseToolAdapter, TOOL_ADAPTERS, create_mock_tool
- `aios/runtime/capability_router.py` — CapabilityRouter (resolve CapabilityRequest→CapabilityResolution, health filter, priority selection, Policy pre-check, fail-closed UNRESOLVED, evidence)
- `aios/capability/capability.py` — extended health to 5-state (UNKNOWN/HEALTHY/DEGRADED/UNHEALTHY/DISABLED) with backward compat
- `aios/runtime/kernel.py` — wire ToolRegistry + CapabilityRouter into Container, health snapshot
- `aios/tool/tests/` — 4 test files (contracts, registry, adapters, architecture) + policy_integration
- `aios/runtime/tests/test_capability_router.py` — kernel wiring tests

Tests: `python -m pytest aios -q` — 1014 passed (163 new + 851 inherited).
