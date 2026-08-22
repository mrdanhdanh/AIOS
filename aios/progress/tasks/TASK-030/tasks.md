# TASK-030 — Breakdown

## Steps
1. Define Verification contracts: Verdict (PASS/FAIL/INCONCLUSIVE), EvidencePackage, VerificationResult
2. Implement VerificationPipeline: add_precondition/add_postcondition/add_invariant, verify() with evidence creation
3. Implement precondition checks: fail → verdict FAIL
4. Implement postcondition checks: fail → verdict FAIL (AC-030-01)
5. Implement invariant checks: violation → FAIL (AC-030-04)
6. Implement Evidence Package creation: every verify() creates EvidencePackage with evidence_id/run_id/checks (AC-030-05)
7. Implement provenance chain: EvidencePackage.run_id → HarnessRun → HarnessSpec (AC-030-06)
8. Implement fail-closed: no checks → INCONCLUSIVE (AC-030-09), not PASS
9. Create `aios/harness/tests/test_verification.py` — 6 tests (all_pass, precondition_fail, postcondition_fail, invariant_fail, no_checks_inconclusive, evidence_created)
10. Run architecture guard — verify no Verification → Runtime implementation direct access
11. Run full suite — 1734/1734 PASS (6 new for verification), no regressions

## Dependencies
- TASK-029 Harness Kernel

## Exit Criteria
- All AC-030-01..10 PASS, gate PASS, no regressions
