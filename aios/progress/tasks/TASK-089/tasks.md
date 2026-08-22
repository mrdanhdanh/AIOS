# Task Breakdown — TASK-089

- [x] BehaviorSurface enum (API/SCHEMA/EVENT/CAPABILITY/TOOL).
- [x] BehaviorScenario dataclass (given/when/then/observable/actual/conforms/evidence).
- [x] BehaviorScenario.is_observable (fail-closed: non-observable → blocked).
- [x] BehaviorHarness.observe (drive + compare actual vs expected).
- [x] BehaviorHarness._record_evidence (T001 provenance via EvidenceStore).
- [x] BehaviorHarness.verify (T030 VerificationPipeline integration).
- [x] BehaviorHarness.is_deterministic + replay_check (T030/T032 ReplayEngine).
- [x] BehaviorConformanceChecker.check (fail-closed suite).
- [x] BehaviorConformanceChecker.to_conformance_report (T087 integration).
- [x] BehaviorConformanceChecker.provenance_complete / result_hash.
- [x] Tests 9 cases (Test Matrix).
- [x] Tích hợp Harness (T030/T032) + Evidence (T001) + Conformance (T087) (import-level).
