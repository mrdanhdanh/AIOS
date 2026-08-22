# TASK-043 — Breakdown

## Steps
1. Create `aios/sdk/contracts.py` — SDKConfig (base_url, api_version, sdk_version, timeout, tenant_id), SDKResponse (success, data, error_code, provenance), ErrorCode enum, SDKError
2. Create `aios/sdk/client.py` — AIOSClient: health, execute (with provenance), list_resources, config property
3. Implement contract synchronization and versioning with compatibility checks
4. Implement error model with provenance for Harness verification
5. Create `aios/sdk/tests/` — 5 tests (config, health, execute, list_resources, error handling)
6. Run architecture guard — verify no SDK → Runtime/Orchestrator implementation imports
7. Run full suite — 1803/1803 PASS (5 new), no regressions

## Dependencies
- TASK-042 Enterprise Operations

## Exit Criteria
- All AC-043-01..10 PASS, gate PASS, no regressions
