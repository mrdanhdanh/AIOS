# TASK-049 — Certification

## Objective
Build the Certification + Trust system for ecosystem extensions/plugins to distinguish unverified, verified, and trusted extensions. Transforms Extension → Registry → Hub into Extension → Validate → Verify → Certify → Trust State → Registry/Hub. Certification is evidence-backed trust decision (not absolute safety), with version, expiry, revocation, and provenance. Fail-closed: no evidence → no certification, UNKNOWN not PASS.

## Scope
### In scope
- Certification contract: certification_id, extension_id, extension_version, certification_version, profile, status, issued_at, expires_at, issuer, evidence_refs, checks, policy/security/compatibility/test results, provenance, signature
- Certification states: UNVERIFIED → VERIFYING → CERTIFIED → EXPIRED → REVOKED (VERIFYING → REJECTED on failure)
- Certification profiles: UNVERIFIED, COMMUNITY, VERIFIED, CERTIFIED, CORE_TRUSTED with required checks/evidence/permissions/compatibility/security/expiry
- Certification checks: Manifest → Contract → Dependency → Compatibility → Permission/Policy → Static Security → Sandbox Test → Conformance Test → Evidence → Decision (deterministic-first, LLM not authority)
- Evidence chain: Certification → Evidence Package → Verification Run → Extension Artifact → Version → Source/Provenance
- Trust decision: CERTIFIED, CERTIFIED_WITH_WARNING, REJECTED, UNKNOWN, EXPIRED, REVOKED (UNKNOWN stays UNKNOWN)
- Revocation: security vulnerability, checksum change, expiry, dependency compromise, contract invalidation, invalid evidence, policy violation
- Certification API and CLI (verify, certify, trust, revoke, evidence)
- Integration with TASK-044–048

### Out of scope
- Replacing Policy/Permission/Credential/Sandbox/Runtime enforcement (certified still goes through all)
- Creating a parallel trust/control plane

## Deliverables
- `aios/certification/contracts.py` — Certification, CertStatus
- `aios/certification/certifier.py` — Certifier (issue, certify, revoke, is_certified, list_certs)
- `aios/certification/tests/` — certification tests

## Acceptance Criteria
- AC-049-01: Extension can go through verification → certification
- AC-049-02: Certification has version, profile, status, expiry
- AC-049-03: Decision only based on valid evidence
- AC-049-04: Missing evidence not auto PASS
- AC-049-05: Artifact change invalidates certification / requires revalidation
- AC-049-06: Revocation works and reflected in Registry/Hub
- AC-049-07: Certification does not grant runtime permission
- AC-049-08: Certified extension still subject to Policy/Permission/Sandbox
- AC-049-09: Certification provenance replayable/auditable
- AC-049-10: Regression M0–M7 PASS

## Dependencies
- TASK-048 — Ecosystem Hub

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
