# TASK-040 — Breakdown

## Steps
1. Create `aios/security/contracts.py` — Credential (cred_id, cred_type, value, expires_at, is_valid), NetworkPolicy (policy_id, name, rules), SandboxConfig (sandbox_id, isolation_level, network_access, filesystem_access)
2. Create `aios/security/isolation.py` — IsolationManager: store/get/validate credentials, add/check network policies, create/get sandboxes
3. Implement credential scope enforcement (tenant/project/capability/TTL)
4. Implement network default-deny and allow-list enforcement
5. Implement sandbox isolation with tenant boundary and reset
6. Create `aios/security/tests/` — 5 tests (credential, network policy, sandbox, isolation, fail-closed)
7. Run architecture guard — verify no Agent → Credential/Network/Sandbox direct access
8. Run full suite — 1788/1788 PASS (5 new), no regressions

## Dependencies
- TASK-039 Quota + Cost

## Exit Criteria
- All AC-040-01..18 PASS, gate PASS, no regressions
