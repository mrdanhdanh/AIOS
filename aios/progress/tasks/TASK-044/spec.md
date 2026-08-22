# TASK-044 — Plugin Runtime

## Objective
Build the Plugin Runtime that loads, manages lifecycle, and isolates plugins/extensions safely via public contracts from TASK-043. Plugin Runtime is not a second Runtime and does not bypass Core Runtime, Capability, Permission, Policy, or Harness. Supports lifecycle DISCOVERED→VALIDATED→INSTALLED→ENABLED→LOADED→RUNNING and DISABLED→UNLOADED→REMOVED with dependency resolution, compatibility checks, and rollback.

## Scope
### In scope
- Plugin manifest and metadata (id, version, api_version, runtime_version, dependencies, capabilities, permissions, resources, entrypoint)
- Plugin discovery/loading and Plugin Registry
- Lifecycle Manager: DISCOVERED→VALIDATED→INSTALLED→ENABLED→LOADED→RUNNING, DISABLED→UNLOADED→REMOVED
- Dependency resolution and compatibility check (contract/schema version)
- Capability declaration and registration via Capability Registry
- Plugin isolation: all actions via Policy→Permission→Capability→Runtime
- Health check, lifecycle failure handling, safe unload/reload, rollback to certified version
- State persistence and integration with Runtime Services, Capability Registry, Policy/Permission, Artifact, Event/Audit, Harness, Public SDK

### Out of scope
- Extension Contracts definition (TASK-045)
- Ecosystem Registry discovery (TASK-046)
- Creating a parallel control plane or second Runtime

## Deliverables
- `aios/plugin_runtime/contracts.py` — PluginSpec, PluginState
- `aios/plugin_runtime/runtime.py` — PluginRuntime (register, load, enable, disable, list, get)
- `aios/plugin_runtime/tests/` — plugin runtime tests

## Acceptance Criteria
- AC-044-01: Plugin lifecycle runs fully and deterministically
- AC-044-02: Plugin does not access private Runtime implementation
- AC-044-03: Plugin does not bypass Capability/Permission/Policy
- AC-044-04: Dependency and compatibility checked before activation
- AC-044-05: Disable/unload removes active capability/runtime binding
- AC-044-06: Upgrade failure has rollback
- AC-044-07: Every lifecycle/security-sensitive action has evidence/audit
- AC-044-08: Plugin failure does not crash Control Plane
- AC-044-09: Harness can verify plugin lifecycle
- AC-044-10: Architecture tests show no boundary violation
- AC-044-11: Regression of M8 and full dependency closure PASS

## Dependencies
- TASK-043 — Public AIOS SDK

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
