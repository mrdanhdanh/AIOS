# TASK-048 — Breakdown

## Steps
1. Create `aios/ecosystem_hub/contracts.py` — HubEntry (entry_id, name, version, status, author, downloads), HubStatus (DRAFT/PUBLISHED/UNPUBLISHED)
2. Create `aios/ecosystem_hub/hub.py` — EcosystemHub: publish (→PUBLISHED), unpublish, download (increment downloads), list_entries, get_entry
3. Implement discovery/search by ID, capability, tag, compatibility
4. Implement compatibility checking and checksum verification
5. Implement revocation handling (revoked not installable)
6. Create `aios/ecosystem_hub/tests/` — 5 tests (publish, unpublish, download, list, get)
7. Run architecture guard — verify no Hub → execution/control-plane
8. Run full suite — 1828/1828 PASS (5 new), no regressions

## Dependencies
- TASK-047 Developer Kit

## Exit Criteria
- All AC-048-01..12 PASS, gate PASS, no regressions
