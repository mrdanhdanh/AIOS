# TASK-046 — Breakdown

## Steps
1. Create `aios/ecosystem_registry/contracts.py` — RegistryEntry (entry_id, name, version, status, author, description), RegistryStatus (PENDING/APPROVED/REJECTED/RETIRED)
2. Create `aios/ecosystem_registry/registry.py` — EcosystemRegistry: register, approve, reject, list_entries (with status filter), get_entry
3. Implement discovery/search by capability/type/version/platform/trust
4. Implement version resolution with semantic versioning and compatibility checking
5. Create `aios/ecosystem_registry/tests/` — 5 tests (register, approve, reject, list, get)
6. Run architecture guard — verify no Registry → execution/control-plane, no Runtime/Tool direct import
7. Run full suite — 1818/1818 PASS (5 new), no regressions

## Dependencies
- TASK-045 Extension Contracts

## Exit Criteria
- All AC-046-01..11 PASS, gate PASS, no regressions
