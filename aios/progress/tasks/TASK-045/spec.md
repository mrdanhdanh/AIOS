# TASK-045 — Extension Contracts

## Objective
Establish stable public extension contracts so extensions/plugins can extend AIOS without depending on Core internal implementation. Extension depends only on public contract (Extension → Public Extension Contract → AIOS SDK/Capability/Runtime API → AIOS Core). Core implementation can change without breaking compliant extensions.

## Scope
### In scope
- Public Extension Contract: metadata, contract_version, api_version, capabilities, dependencies, permissions, lifecycle, configuration, compatibility
- Extension types: Tool, Capability, Skill, Workflow, Prompt, Agent, Integration (no separate runtime per type)
- Lifecycle contract: DISCOVERED→VALIDATED→INSTALLED→ENABLED→LOADED→RUNNING→UNLOADED/DISABLED→REMOVED with init/activation/deactivation/unload/cleanup/failure
- Contract boundary: Extension can access Public SDK/Capability/Runtime/Event/Artifact/Configuration APIs; cannot import Runtime Service implementation, access DB, bypass Permission/Policy, call Tool directly, modify Registry, access Event Bus impl, access filesystem outside boundary
- Versioning: MAJOR.MINOR semantic (MINOR backward-compatible, MAJOR breaking), compatibility check before enable/load, fail-closed on UNKNOWN
- Capability/Permission declaration (need, not grant) via Capability Registry and Policy/Permission services
- Compatibility model: Extension ID, Version, Contract Version, API Version, Required Capabilities/Permissions, Dependencies, AIOS range → COMPATIBLE/INCOMPATIBLE/UNKNOWN (UNKNOWN→BLOCK)
- Public vs Internal API separation with architecture tests

### Out of scope
- Plugin Runtime lifecycle implementation (TASK-044)
- Ecosystem Registry discovery (TASK-046)
- Creating a parallel control plane

## Deliverables
- `aios/extension_contracts/contracts.py` — ExtensionSpec, ExtensionManifest, CapabilityExport
- `aios/extension_contracts/validator.py` — ExtensionValidator (validate_spec, validate_capability)
- `aios/extension_contracts/tests/` — extension contracts tests

## Acceptance Criteria
- AC-045-01: Public extension contract stable and versioned
- AC-045-02: Extension types supported via single contract
- AC-045-03: Lifecycle contract defined and enforced
- AC-045-04: Extension cannot access internal Runtime implementation
- AC-045-05: Versioning with compatibility check (UNKNOWN→BLOCK)
- AC-045-06: Capability declaration is need, not grant
- AC-045-07: Permission declaration not authorization
- AC-045-08: Compatibility model deterministic
- AC-045-09: Public vs Internal API separated and tested
- AC-045-10: Regression M0–M7 PASS

## Dependencies
- TASK-044 — Plugin Runtime

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
