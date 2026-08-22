# TASK-064 — Implementation

Real source lives in the new package **`aios/contracts/`** (this folder is only
a pointer, per the task standard).

## Modules
- `aios/contracts/contract.py` — `Contract` dataclass (name, version default
  `"1.0.0"`, status, surface, compatibility, evidence_ref) plus `ContractStatus`
  (`FROZEN|DRAFT|DEPRECATED`) and `ContractSurface`
  (`API|SCHEMA|EVENT|CAPABILITY|TOOL`) enums with SemVer validation.
- `aios/contracts/registry.py` — `ContractRegistry` with `register` / `lookup` /
  `freeze` / `deprecate`; `ContractFreezeError` (no silent change) and
  `ContractNotRegisteredError` (no shadow contract); `build_default_registry`
  populates the five 1.0 surfaces, all `FROZEN` at `1.0.0`.
- `aios/contracts/conformance.py` — `check_contract_conformance` /
  `check_registry_conformance` (violation list, fail-closed) and
  `require_conformance` (raises `ConformanceError`).
- `aios/contracts/tests/test_contracts.py` — conformance + freeze-safety tests.

## Freeze policy (enforced)
- A `FROZEN` contract may not change at the same version (silent change →
  `ContractFreezeError`).
- Any change to a `FROZEN` contract requires an `adr_ref`.
- A breaking change (major version bump) additionally opens a deprecation window
  (`DEFAULT_DEPRECATION_WINDOW = "180d"`).

## Compatibility promise
Backward-compatible until the next major version (e.g. `compatibility="2.0.0"`).
Documented by ADR `adr:T064-public-contract-freeze`.
