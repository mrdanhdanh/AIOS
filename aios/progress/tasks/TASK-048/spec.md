# TASK-048 — Ecosystem Hub

## Objective
Build the Ecosystem Hub as the official distribution layer for extensions/skills/plugins. Enables publish, discover/search, metadata/version/dependency/capability/permission viewing, compatibility checking, download/install via Plugin Runtime, version management, and lifecycle distribution — without bypassing Runtime, Policy, Permission, or Certification. Hub is distribution plane, not execution/control plane.

## Scope
### In scope
- Extension Package: manifest.yaml, contracts, skills, capabilities, prompts, workflows, assets, metadata
- Hub Registry: identity, versions, metadata, dependencies, capabilities, permissions, compatibility, certification, checksum, distribution artifact (publish, unpublish/revoke, version lookup, search, filtering, dependency metadata, compatibility query)
- Discovery: deterministic search by ID, exact name, capability, category/tag, compatibility, certification/trust (no LLM dependency)
- Distribution: Package → Validate → Publish → Hub → Discover → Compatibility Check → Certification/Trust Check → Download → Plugin Runtime → Policy+Permission → Install/Enable (Hub distributes artifact, Plugin Runtime handles lifecycle)
- Compatibility: AIOS version, Contract version, Extension API version, Required capabilities/permissions, Dependencies, Platform constraints (incompatible → blocked/marked, not silently installed)
- Security: Hub does not grant permission, execute tool, resolve credential, auto-enable plugin, bypass certification; artifact has checksum/provenance; revoked not installable

### Out of scope
- Rebuilding registry, runtime, or certification (consumes TASK-044–047 contracts)
- Creating a parallel execution/control plane

## Deliverables
- `aios/ecosystem_hub/contracts.py` — HubEntry, HubStatus
- `aios/ecosystem_hub/hub.py` — EcosystemHub (publish, unpublish, download, list, get)
- `aios/ecosystem_hub/tests/` — ecosystem hub tests

## Acceptance Criteria
- AC-048-01: Valid extension can publish and appear in registry
- AC-048-02: Invalid manifest/package wrong schema → REJECT
- AC-048-03: Published extension_id+version immutable (no silent overwrite)
- AC-048-04: Can find extension by ID, capability, tag, compatibility
- AC-048-05: Incompatible extension → INCOMPATIBLE, not installable
- AC-048-06: Downloaded artifact verifies checksum before Plugin Runtime handoff
- AC-048-07: Hub does not directly execute plugin/tool
- AC-048-08: Install/enable continues via Plugin Runtime + Policy + Permission
- AC-048-09: Every distributed artifact traceable (Extension→Version→Artifact→Checksum→Publisher→Certification/Trust)
- AC-048-10: Revoked extension/version not trusted/installable
- AC-048-11: Local/cache registry serves discovery and cached artifacts when offline
- AC-048-12: Regression M0–M7 PASS, no invariant violation

## Dependencies
- TASK-047 — Developer Kit

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
