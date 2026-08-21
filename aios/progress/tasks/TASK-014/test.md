# TASK-014 — Test Report

## Suites

| Suite | File | Cases | Result |
|-------|------|-------|--------|
| tool contracts | `aios/tool/tests/test_contracts.py` | 32 | PASS |
| tool registry | `aios/tool/tests/test_registry.py` | 38 | PASS |
| tool adapters | `aios/tool/tests/test_adapters.py` | 42 | PASS |
| tool router | `aios/tool/tests/test_router.py` | 38 | PASS |
| policy integration | `aios/tool/tests/test_policy_integration.py` | 10 | PASS |
| tool architecture | `aios/tool/tests/test_architecture.py` | 8 | PASS |
| capability router (kernel) | `aios/runtime/tests/test_capability_router.py` | 7 | PASS |
| full harness | `python -m pytest aios -q` | 1014 | PASS |

## Coverage

- **ToolContract**: 6 ToolTypes (python/docker/rest/mcp/shell/git), 5 health states (UNKNOWN/HEALTHY/DEGRADED/UNHEALTHY/DISABLED) with UNKNOWN fail-closed, version SemVer, capability declaration (single/multi), permissions/resources, priority/enabled, to_dict, provenance, contract check.
- **ToolRegistry**: register/get/list, duplicate/unknown reject, unregister, clear, capability declaration (single/multi), dynamic discovery Capability→Tool[] (no hard-code), multi-tool capability (priority desc), enable/disable, health (5-state), priority, metadata, version/compatibility, find, capabilities list, thread-safety (concurrent register/lookup), evidence mapping.
- **Tool Adapters**: BaseToolAdapter (health/availability, execute success/failure, disabled/unhealthy/unknown reject, timeout/failure simulation, call_count), PythonTool (execute_code/run_python/run_tests), DockerTool (execute_container/run_python/run_tests), RestTool (http_request/call_api), McpTool (mcp_call/call_tool), ShellTool (execute_shell/run_command, never real subprocess), GitTool (git_read/diff/status/commit), TOOL_ADAPTERS registry (6 types), create_mock_tool (all types, custom caps), offline (no network/subprocess).
- **CapabilityRouter**: single/multi tool resolved, priority deterministic (higher wins, seq tie-break), health-aware (HEALTHY/DEGRADED eligible, UNHEALTHY/DISABLED/UNKNOWN reject, fail-closed), priority-aware (higher wins, not override health), policy-aware (ALLOW/DENY/ASK, DENY skip to next, priority not override DENY, ASK no auto-execute), fail-closed (capability not exist, no tool, invalid request, resolve_or_raise), constraints (tool_type/sandbox/network), evidence (candidates/reason/evidence_ref), offline (no policy, mock tools), fallback only after policy.
- **Policy Integration**: pre-check before selection, allow then execute, deny no fallback, ASK no auto-execute, permission gate fail-closed, shell deny, priority not bypass, fallback only when allowed, tool does not bypass policy, router does not execute.
- **Architecture**: tool does not import runtime/agent/orchestrator/capability/worker, only core/stdlib, no subprocess, router at runtime layer (may import tool/capability, not agent/orchestrator), worker/agent do not import tool, router is resolver not executor, guard PASS.
- **Kernel Wiring**: ToolRegistry + CapabilityRouter singletons, health includes tools, isolated per container, shared policy, full health after population, mock adapters via kernel.
- `python -m pytest aios -q` — 1014 passed, 0 failed.

## AC mapping

| AC | Cases | Result |
|----|-------|--------|
| AC-014-01 Tool Contract | test_contracts (32) | PASS |
| AC-014-02 Capability Declaration | test_registry::test_tool_declares_* + test_contracts::test_tool_contract_multiple_capabilities | PASS |
| AC-014-03 Dynamic Discovery | test_registry::test_dynamic_discovery_* | PASS |
| AC-014-04 Multi-Tool Capability | test_registry::test_multi_tool_* | PASS |
| AC-014-05 Health-aware Routing | test_router::test_router_health_* | PASS |
| AC-014-06 Priority-aware Routing | test_router::test_router_priority_* | PASS |
| AC-014-07 Policy-aware Routing | test_router::test_router_policy_* + test_policy_integration | PASS |
| AC-014-08 Fail-Closed | test_router::test_router_capability_not_exist + test_router::test_router_no_tool + test_router::test_router_invalid_request | PASS |
| AC-014-09 Worker Isolation | test_architecture::TestWorkerIsolation + test_architecture::TestToolLayering | PASS |
| AC-014-10 Offline | test_router::test_router_offline_* + test_adapters::test_adapters_offline | PASS |
| AC-014-11 Evidence | test_router::test_router_evidence_* + test_registry::test_list_capabilities_evidence | PASS |
| AC-014-12 Regression | full harness 1014 | PASS |
