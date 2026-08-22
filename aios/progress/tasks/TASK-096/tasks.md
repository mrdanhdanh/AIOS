# Task Breakdown — TASK-096

- [x] SimulationGate enum (PASS/REJECT).
- [x] Sandbox dataclass (sandbox_id, isolation, fail-closed).
- [x] SimulationResult dataclass (candidate_id, sandbox_id, observed_outcome, meta_verified, gate, evidence_ref).
- [x] SimulationEngine.simulate (sandbox isolation + observe via VerificationPipeline T030).
- [x] SimulationEngine._default_sim (deterministic default outcome).
- [x] SimulationGateEngine.run (simulate + meta-verify T091 + fail-closed gate).
- [x] SimulationGateEngine._record_evidence (T001 provenance via EvidenceStore).
- [x] SimulationGateEngine.provenance_complete / result_hash.
- [x] Tests 7 cases (Test Matrix).
- [x] Tích hợp Candidate (T095) + Meta (T091) + Harness (T030/T032) (import-level).
