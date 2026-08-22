# TASK-040 — Credential + Network + Sandbox Isolation

## Objective
Build the Security & Data Isolation layer ensuring every credential, network access, and untrusted execution is controlled by Identity → Tenant → Policy → Permission → Capability → Runtime. Agent/Tool never holds, resolves, or bypasses credential, network policy, or sandbox. Enforces INV-023 Tenant Isolation, INV-024 Credential Isolation, INV-028 Sandbox Boundary.

## Scope
### In scope
- Credential Broker: scoped resolution (tenant/project/capability/TTL/revocation), short-lived scoped credentials, audit integration
- Credential Scope: tenant, project, capability, principal, TTL, allowed action, revocation, audit ref
- Credential Resolution: 8 checks (principal, tenant, project, capability, action, policy, validity, scope compatibility) — fail-closed
- Network Policy: default-deny, destination/protocol/port/direction/tenant/project/capability/environment, enforcement at execution boundary
- Sandbox Isolation: filesystem/network/resource isolation, timeout, cleanup/reset, tenant isolation, reuse with reset
- Security contracts: CredentialRequest, CredentialGrant, NetworkRequest, NetworkDecision, SandboxRequest, SandboxGrant
- Audit & Evidence for all security-sensitive actions (no plaintext secrets in logs)

### Out of scope
- Creating a parallel security control plane
- Replacing Policy/Permission/Capability services
- Distributed security (M7+)

## Deliverables
- `aios/security/contracts.py` — Credential, NetworkPolicy, SandboxConfig
- `aios/security/isolation.py` — IsolationManager (credentials, network policies, sandboxes)
- `aios/security/tests/` — security isolation tests

## Acceptance Criteria
- AC-040-01: Credential Broker works per scope
- AC-040-02: Credential has TTL and revocation
- AC-040-03: Cross-tenant credential access DENY
- AC-040-04: Agent/Tool does not hold credential directly
- AC-040-05: Network default-deny enforced
- AC-040-06: Network allow-list works per policy
- AC-040-07: Untrusted execution requires sandbox
- AC-040-08: Sandbox isolates filesystem/network/resource
- AC-040-09: Sandbox reset between executions
- AC-040-10: Security events have audit/evidence
- AC-040-11: Secret not in plaintext log/evidence
- AC-040-12: Policy failure → fail-closed
- AC-040-13: INV-023, INV-024, INV-028 tested automatically
- AC-040-14: Regression M1–M6 PASS
- AC-040-15: Architecture tests PASS
- AC-040-16: Harness verification PASS
- AC-040-17: Evidence with provenance
- AC-040-18: UNKNOWN not promoted to PASS

## Dependencies
- TASK-039 — Quota + Cost + Resource Governance

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-023 Tenant Isolation, INV-024 Credential Isolation, INV-028 Sandbox Boundary enforced.
