# TASK-064 — Critique 1

## Strengths
- Scope is correctly limited to freeze + versioning + documentation (no new behavior).
- The `Contract` model matches the T064 spec field-for-field (name, version, status, surface, compatibility, evidence_ref).
- Freeze-safety is enforced fail-closed via `ContractFreezeError`, satisfying "no silent change".

## Risks / Gaps
- The spec lists `status(FROZEN|DRAFT|DEPRECATED)` and `surface(API|SCHEMA|EVENT|CAPABILITY|TOOL)`; the model must use enums so invalid values are rejected.
- "Breaking change requires major bump + ADR + deprecation window" — the deprecation window must be recorded, not just implied.
- Conformance must be *fail-closed*: a missing surface or missing evidence must produce a non-empty violation list and block DONE.
- Determinism must be explicit (same registry + same test → same result) to satisfy AC-064-07.

## Required revisions
- Add `ContractStatus` / `ContractSurface` enums with validation in `__post_init__`.
- Record the deprecation window in the registry on a major bump.
- Provide `check_registry_conformance` returning a violation list + `require_conformance` that raises.
- Add explicit determinism tests.
