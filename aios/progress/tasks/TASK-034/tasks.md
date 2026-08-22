# TASK-034 — Breakdown

## Steps
1. Create `aios/harness/doctor.py` — DoctorVerdict (PASS/WARNING/ERROR/UNKNOWN with is_healthy), DoctorCheck, DiagnosisReport, HarnessDoctor (register, diagnose), ReadinessChecker (add_check, is_ready fail-closed)
2. Implement HarnessDoctor.diagnose: aggregate verdicts (ERROR > WARNING > PASS > UNKNOWN), handle exceptions → ERROR
3. Implement ReadinessChecker.is_ready: fail-closed (all checks must pass, no checks → False)
4. Create `aios/harness/tests/test_doctor.py` — 7 tests (all pass, with error, exception handling, is_healthy, readiness all pass/one fail/no checks)
5. Run architecture guard — verify no Harness → Runtime implementation
6. Run full suite — 1756/1756 PASS (7 new), no regressions

## Dependencies
- TASK-033 Benchmark + Regression Gate

## Exit Criteria
- All AC-034-01..14 PASS, gate PASS, no regressions
