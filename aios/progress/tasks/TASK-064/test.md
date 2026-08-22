# TASK-064 — Test Report

## How to run
```
python -m pytest aios/contracts -q
```

## What is covered
- Default 1.0 registry: five FROZEN surfaces, all `version=1.0.0` (AC-064-01, AC-064-03).
- Lookup of a registered contract; unregistered public surface raises
  `ContractNotRegisteredError` (no shadow contract) (AC-064-03).
- Freeze safety:
  - silent change (same version) → `ContractFreezeError` (AC-064-05);
  - breaking change without ADR → `ContractFreezeError` (AC-064-02, AC-064-06);
  - breaking change with ADR + major bump → allowed, opens deprecation window (AC-064-02);
  - non-breaking change with ADR → allowed (AC-064-05);
  - DRAFT contracts may change without ADR (negative control).
- Freeze transition requires `adr_ref`; deprecate marks `DEPRECATED`.
- Conformance fail-closed: missing surface / missing evidence / missing
  compatibility → non-empty violation list and `require_conformance` raises (AC-064-04, AC-064-06).
- Determinism: same registry + same test → same result; same register sequence
  → same state (AC-064-07).

## Results
- `aios/contracts`: 17 passed
- Architecture guard: `aios/contracts` is `unknown` layer, stdlib-only internals → no violations.
- Status: ALL PASS
