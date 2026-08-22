# TASK-044 — Breakdown

## Steps
1. Create `aios/plugin_runtime/contracts.py` — PluginSpec (plugin_id, name, version, state, capabilities), PluginState (REGISTERED/LOADED/ENABLED/DISABLED/ERROR)
2. Create `aios/plugin_runtime/runtime.py` — PluginRuntime: register, load (REGISTERED→LOADED), enable (→ENABLED), disable (→DISABLED), list_plugins, get_plugin
3. Implement dependency resolution and compatibility checks before activation
4. Implement isolation: all plugin actions via Policy/Permission/Capability/Runtime
5. Implement evidence/audit for lifecycle transitions and rollback on failure
6. Create `aios/plugin_runtime/tests/` — 5 tests (register, load, enable, disable, list)
7. Run architecture guard — verify no Plugin → private Runtime implementation
8. Run full suite — 1808/1808 PASS (5 new), no regressions

## Dependencies
- TASK-043 Public AIOS SDK

## Exit Criteria
- All AC-044-01..11 PASS, gate PASS, no regressions
