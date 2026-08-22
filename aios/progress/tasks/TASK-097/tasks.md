# Task Breakdown — TASK-097

- [x] ApplyResult dataclass (candidate_id, permission_granted, human_approved, applied, re_test_passed, rolled_back, certified, evidence_ref, reason).
- [x] ApplyOrchestrator._risk_level (T054/T067 autonomy risk classification).
- [x] ApplyOrchestrator.apply (simulation gate -> permission -> approval -> apply -> re-test -> rollback -> certify).
- [x] ApplyOrchestrator._re_test (harness re-test T030/T032, deterministic default).
- [x] ApplyOrchestrator._rollback (T074/T066, audit trail).
- [x] ApplyOrchestrator._certify (T073 Certifier).
- [x] ApplyOrchestrator._record_evidence (T001 provenance via EvidenceStore).
- [x] ApplyOrchestrator.provenance_complete / result_hash.
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Simulation (T096) + Permission (T070) + Governor (T054) + Harness + Certification (T073) (import-level).
