# TASK-046 — Ecosystem Registry

## Objective
Build the Ecosystem Registry as the central discovery layer for all external extensions/plugins/skills/components. Provides metadata and public extension contract reading, search/filter by capability/version/compatibility/platform/trust, version resolution, and compatibility checking before runtime. Registry is discovery/metadata only — not execution.

## Scope
### In scope
- Registry contract: extension (id, name, version, type, description, author, license, capabilities, dependencies, compatibility, platforms, trust, artifact checksum) with schema validation and versioning
- Registration: register, update, unregister, get, list, search, resolve (reject duplicate ID, invalid metadata/version, incompatible contract, checksum mismatch)
- Discovery: by extension_id, type, capability, version, AIOS compatibility, platform, trust/certification, author, tag
- Version resolution: semantic version (^1.2.0 → 1.3.0), no auto downgrade/upgrade outside constraint, RESOLUTION_FAILED if no compatible version
- Compatibility: Extension/AIOS/Contract/Schema/Platform/Dependency → COMPATIBLE/INCOMPATIBLE/UNKNOWN (UNKNOWN not COMPATIBLE)
- Trust metadata: UNVERIFIED/VERIFIED/CERTIFIED/REVOKED (input to Policy/Certification, not execution grant)
- Persistence/index consistency

### Out of scope
- Marketplace/distribution platform (TASK-048)
- Certification engine (TASK-049)
- Plugin runtime lifecycle (TASK-044)
- Creating a parallel control plane or execution subsystem

## Deliverables
- `aios/ecosystem_registry/contracts.py` — RegistryEntry, RegistryStatus
- `aios/ecosystem_registry/registry.py` — EcosystemRegistry (register, approve, reject, list, get)
- `aios/ecosystem_registry/tests/` — registry tests

## Acceptance Criteria
- AC-046-01: Valid extension can register and retrieve by immutable ID
- AC-046-02: Duplicate ID → REJECT (no silent overwrite)
- AC-046-03: Search by capability/type/version returns correct extensions
- AC-046-04: Same input + same registry state → same resolution (deterministic)
- AC-046-05: Incompatible extension → INCOMPATIBLE, not executable candidate
- AC-046-06: UNKNOWN not promoted to PASS/CERTIFIED/COMPATIBLE
- AC-046-07: Checksum mismatch detected
- AC-046-08: Registry does not bypass Policy/Permission/Capability/Runtime
- AC-046-09: Version resolver respects constraints, rejects incompatible, no breaking major
- AC-046-10: Architecture — no execution/control-plane, no Runtime/Tool direct import
- AC-046-11: Regression of TASK-043/044/045 PASS

## Dependencies
- TASK-045 — Extension Contracts

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
