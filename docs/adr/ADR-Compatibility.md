# ADR-Compatibility — AIOS 1.x Versioning & Compatibility Policy

- **Status:** ACCEPTED
- **Date:** 2026-08-22
- **Supersedes:** —
- **Superseded by:** —
- **Related tasks:** T084 (Version Baseline), T085 (Migration 1.0→1.1),
  T086 (Backward Compatibility), T087 (Conformance), T088 (Docs & ADR)
- **Related ADR:** ADR-ARCH-1.0 (Architecture 1.0 Freeze)

## 1. Context

AIOS 1.0 has shipped with a frozen public contract surface (T064) and an
architecture freeze (ADR-ARCH-1.0). As the system evolves toward 1.1 and beyond,
we need an explicit, enforceable policy that answers:

* When is a change a **MAJOR / MINOR / PATCH** bump?
* How do we keep **1.0 consumers working** on 1.x?
* What is the **deprecation window** before a breaking change lands?
* How do we **prove** a build is compatible (conformance)?

Without this policy, breaking changes could land silently and break existing
integrations — violating the trust/evidence guarantees of the platform.

## 2. Decision

We adopt **Semantic Versioning (semver, MAJOR.MINOR.PATCH)** as the single
versioning scheme for AIOS 1.x, with the following rules:

1. **Breaking change → MAJOR.** Any change that breaks a 1.0 consumer (API,
   schema, or event surface) MUST bump the MAJOR version and MUST NOT be silent.
2. **Backward-compatible change → MINOR.** New, non-breaking capabilities on the
   same MAJOR line (1.x) are MINOR bumps.
3. **Fix → PATCH.** Bug fixes and internal changes that preserve behavior are
   PATCH bumps.
4. **Deprecation window.** A breaking (MAJOR) change MUST be announced with a
   deprecation notice of at least **180 days** (`DEFAULT_DEPRECATION_WINDOW`,
   inherited from T064) before the old surface is removed.
5. **Compatibility matrix.** A target version is backward-compatible with a base
   version iff they share the same MAJOR component and `target >= base`. 1.0 is
   therefore compatible with every 1.x; 2.0 is a breaking release.
6. **Provenance.** Every version policy decision and compat/conformance check
   carries an `evidence_ref` (T001 Rule 5).
7. **Conformance gate.** A build is only declared *compatible* after passing the
   full conformance suite (T087): api / schema / event / version / contract. One
   failing check → not conformant (fail-closed).

## 3. Rationale

* **semver** is the industry-standard, deterministic scheme — the same change
  type always yields the same bump, which makes automation (migration, conformance)
  predictable.
* **No silent breaking** protects the large installed base of 1.0 consumers and
  preserves the trust guarantees of AIOS.
* **180-day deprecation** gives integrators a predictable migration window,
  matching the contract-freeze window from T064.
* **Conformance as a gate** (not a report-only artifact) ensures compatibility is
  *enforced*, not merely documented.

## 4. Consequences

* All version bumps are classified by `VersionPolicyEngine` (T084) — breaking
  changes without ADR + deprecation are rejected (fail-closed).
* Migration 1.0→1.1 (T085) is reversible and dry-runable; verify FAIL → never apply.
* Backward compatibility (T086) blocks any breaking change against a 1.0 consumer.
* Conformance (T087) issues a certificate only for fully conformant builds (T073).
* Documentation (T088) records this policy and its rationale for developers (T071 DX).

## 5. Integration map

| Capability | Module | Task |
|------------|--------|------|
| Version policy + matrix | `aios/versioning` | T084 |
| Migration 1.0→1.1 | `aios/migration` | T085 |
| Backward compatibility | `aios/backward_compat` | T086 |
| Conformance harness | `aios/conformance` | T087 |
| Docs & ADR review | `aios/compat_docs` | T088 |
