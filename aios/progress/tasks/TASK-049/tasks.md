# TASK-049 — Breakdown

## Steps
1. Create `aios/certification/contracts.py` — Certification (cert_id, target_id, status, issued_at, expires_at, issuer), CertStatus (PENDING/CERTIFIED/REVOKED/EXPIRED)
2. Create `aios/certification/certifier.py` — Certifier: issue, certify (PENDING→CERTIFIED), revoke (→REVOKED), is_certified, list_certs
3. Implement certification checks pipeline (Manifest→Contract→Dependency→Compatibility→Policy→Security→Sandbox→Conformance→Evidence→Decision)
4. Implement evidence chain and trust decision (CERTIFIED/REJECTED/UNKNOWN/EXPIRED/REVOKED)
5. Implement revocation and Registry/Hub reflection
6. Create `aios/certification/tests/` — 5 tests (issue, certify, revoke, is_certified, list)
7. Run architecture guard — verify no Certification → Policy/Permission/Sandbox bypass
8. Run full suite — 1833/1833 PASS (5 new), no regressions

## Dependencies
- TASK-048 Ecosystem Hub

## Exit Criteria
- All AC-049-01..10 PASS, gate PASS, no regressions
