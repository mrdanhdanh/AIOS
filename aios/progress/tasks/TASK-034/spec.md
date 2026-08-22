# TASK-034 — Doctor + Readiness

## Objective
Upgrade `aiagent doctor` + `aiagent arch-health` into the AIOS Doctor Harness with fail-closed Readiness. Doctor checks 13 domains (Architecture, Runtime, Workflow, Agent, Capability, Tool, Memory, Model, Policy, Registry, Performance, Security, Evidence) with verdicts PASS/WARNING/ERROR/UNKNOWN. Readiness combines scores, hard gates, required checks, and evidence completeness into READY/READY_WITH_WARNINGS/BLOCKED/UNKNOWN — UNKNOWN never promoted to READY.

## Scope
### In scope
- Doctor contracts: DoctorCheck, DiagnosisReport, DoctorVerdict (PASS/WARNING/ERROR/UNKNOWN)
- HarnessDoctor: register checks, diagnose (aggregate verdicts: ERROR > WARNING > PASS > UNKNOWN)
- ReadinessChecker: fail-closed readiness (any check failure → not ready, no checks → not ready)
- 13 domain checks with evidence provenance
- Hard gates (policy violation, architecture violation, evidence failure → BLOCKED)
- CLI: `aiagent harness doctor`, `aiagent harness readiness` (compat with `aiagent doctor`, `aiagent arch-health`)
- Evidence Package per Doctor Run

### Out of scope
- Creating an independent Doctor subsystem (upgrades existing doctor/arch-health)
- Distributed doctor (M7)
- Auto-remediation (beyond diagnosis)

## Deliverables
- `aios/harness/doctor.py` — HarnessDoctor, ReadinessChecker, DoctorCheck, DiagnosisReport, DoctorVerdict
- `aios/harness/tests/test_doctor.py` — doctor and readiness tests

## Acceptance Criteria
- AC-034-01: Doctor checks all required domains
- AC-034-02: Each check has verdict PASS/WARNING/ERROR/UNKNOWN
- AC-034-03: Important verdicts have evidence provenance
- AC-034-04: UNKNOWN not promoted to PASS
- AC-034-05: Readiness has score and hard gates
- AC-034-06: Critical policy violation blocks readiness
- AC-034-07: Architecture violation blocks readiness
- AC-034-08: Evidence failure blocks readiness
- AC-034-09: Doctor does not bypass Runtime/Policy boundary
- AC-034-10: CLI doctor and readiness work
- AC-034-11: Regression M0–M5 + M6 PASS
- AC-034-12: INV-017..021 enforced
- AC-034-13: Evidence sufficient for replay/audit
- AC-034-14: Readiness deterministic with same input/evidence

## Dependencies
- TASK-033 — Benchmark + Regression Gate

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-017..021 enforced.
