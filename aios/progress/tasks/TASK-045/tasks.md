# TASK-045 — Breakdown

## Steps
1. Create `aios/extension_contracts/contracts.py` — ExtensionSpec (spec_id, name, version, capabilities), ExtensionManifest (manifest_id, extension, author, license), CapabilityExport
2. Create `aios/extension_contracts/validator.py` — ExtensionValidator: validate_spec (name/version required), validate_capability (name required)
3. Implement versioning and compatibility model (COMPATIBLE/INCOMPATIBLE/UNKNOWN, UNKNOWN→BLOCK)
4. Implement public vs internal API separation
5. Create `aios/extension_contracts/tests/` — 5 tests (spec, manifest, capability, validation, compatibility)
6. Run architecture guard — verify no Extension → Runtime implementation
7. Run full suite — 1813/1813 PASS (5 new), no regressions

## Dependencies
- TASK-044 Plugin Runtime

## Exit Criteria
- All AC-045-01..10 PASS, gate PASS, no regressions
