# TASK-064 — Public Contract Freeze

## Objective
Freeze the AIOS 1.0 public contracts so that the externally-visible API, schema,
event, capability and tool surfaces are versioned and committed to a
backward-compatibility promise. TASK-064 is **contract freeze + versioning +
documentation**, not a new feature. It builds on the Architecture 1.0 baseline
(T063) and locks behavior so downstream consumers can rely on stability.

## Scope
**In scope**
- A `Contract` model (name, version, status, surface, compatibility, evidence_ref).
- A `ContractRegistry` enforcing freeze safety (no silent change; breaking
  change requires major bump + ADR + deprecation window).
- Population of the registry with the five 1.0 surfaces (api/schema/event/
  capability/tool), all `FROZEN` at `1.0.0`.
- Conformance tests that lock frozen-contract behavior (fail-closed, deterministic).

**Out of scope**
- New runtime behavior, new provider/tool features, or changes to existing
  public surfaces. This task only *documents and locks* what already exists.

## Deliverables
- `aios/contracts/contract.py` — `Contract` dataclass + `ContractStatus`/`ContractSurface`.
- `aios/contracts/registry.py` — `ContractRegistry` (register/lookup/freeze/
  deprecate) + `ContractFreezeError`/`ContractNotRegisteredError` + `build_default_registry`.
- `aios/contracts/conformance.py` — `check_contract_conformance` / `check_registry_conformance` / `require_conformance`.
- `aios/contracts/tests/test_contracts.py` — conformance + freeze-safety tests.
- Compatibility promise (documented in this folder + ADR reference `adr:T064-public-contract-freeze`).

## Acceptance Criteria
- AC-064-01: Every public contract has `version=1.0.0`, `status=FROZEN`.
- AC-064-02: A breaking change requires a major bump + ADR + deprecation window.
- AC-064-03: Every public surface (API/SCHEMA/EVENT/CAPABILITY/TOOL) has a registered contract.
- AC-064-04: Contract conformance tests PASS.
- AC-064-05: Changing a contract forces a version bump (no silent change).
- AC-064-06: A failing contract test BLOCKS (fail-closed).
- AC-064-07: Contract tests are deterministic (same version + test → same result).
- AC-064-08: Regression of prior milestones stays green; no invariant violation.

## Dependencies
- TASK-063 (AIOS Architecture 1.0) — freeze is performed on the 1.0 architecture.

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`; architecture guard classifies
  `aios/contracts` as `unknown` (no upward imports; stdlib-only internals).
