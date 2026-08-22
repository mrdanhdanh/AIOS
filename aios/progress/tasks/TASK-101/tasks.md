# Task Breakdown — TASK-101

- [x] CertGate enum (governance/architecture/contract/harness/conformance).
- [x] ContinuousCertRun dataclass (change_id, gates_run, all_passed, deploy_allowed, gate_results, evidence_ref).
- [x] ContinuousCertEngine.trigger_on_change (T062/T099, fail-closed re-run).
- [x] ContinuousCertEngine.run_suite (5 gates, fail-closed deploy).
- [x] ContinuousCertEngine._record_evidence (T001 provenance).
- [x] ContinuousCertEngine.provenance_complete / result_hash.
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Certification + Conformance + Coverage + Meta + Trust + Evidence (import-level).
