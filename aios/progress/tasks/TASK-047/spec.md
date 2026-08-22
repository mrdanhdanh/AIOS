# TASK-047 — Developer Kit

## Objective
Build the AIOS Developer Kit (ADK) for creating, developing, and testing extensions via public contracts. Provides project generator, manifest validation, contract compatibility checking, local test integration, Harness simulation, packaging, and inspection — all via public contract/API without bypassing Runtime/Policy.

## Scope
### In scope
- Extension project generator: skeleton with aios.extension.yaml, pyproject.toml, src/, tests/, README.md for Tool/Capability/Skill/Workflow/Agent types
- Extension Manifest: id, name, version, type, aios contract_version, dependencies, capabilities, permissions, resources, entrypoint with fail-closed validation
- CLI: `aios dev create`, `validate`, `test`, `simulate`, `package`, `inspect`
- Local development loop: Edit → Validate → Test → Simulation → Evidence → Package
- Contract validation: Metadata, Contract Version, Schema, Dependencies, Capabilities, Permissions, Resources, Entrypoint
- Test integration: orchestration via pytest/vitest → Harness → Evidence (not replacing test runners)
- Simulation via Harness M6 (no separate simulation engine)
- Packaging: immutable artifact with manifest, version, checksum, dependency/capability/permission metadata, evidence

### Out of scope
- Creating a new runtime (uses existing Plugin Runtime, Extension Contracts, Registry)
- Replacing Harness or Runtime

## Deliverables
- `aios/devkit/contracts.py` — ProjectTemplate, ScaffoldConfig
- `aios/devkit/scaffold.py` — DevKitScaffold (register_template, get_template, scaffold, list_templates)
- `aios/devkit/tests/` — devkit tests

## Acceptance Criteria
- AC-047-01: `aios dev create example` creates valid skeleton that validates immediately
- AC-047-02: Valid manifest → PASS, invalid/missing field/wrong schema/incompatible → FAIL (fail-closed)
- AC-047-03: Only contract-compatible extensions can build/package
- AC-047-04: `aios dev test` runs extension test suite with provenance
- AC-047-05: `aios dev simulate` runs via Harness simulation without real side effects
- AC-047-06: Package creates artifact with manifest, version, checksum, dependency/capability/permission metadata, evidence
- AC-047-07: Invalid manifest/incompatible contract/unknown capability/invalid permission/broken dependency → not valid
- AC-047-08: Architecture test proves no bypass of Policy/Permission/Capability/Runtime/Harness
- AC-047-09: Deterministic validation (rule/schema) without LLM
- AC-047-10: Regression M0–M7 PASS

## Dependencies
- TASK-046 — Ecosystem Registry

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
