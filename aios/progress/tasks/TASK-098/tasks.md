# Task Breakdown — TASK-098

- [x] RemediationArtifact dataclass (artifact_id, content, expected_hash, is_tampered).
- [x] RemediationIntegrity dataclass (remediation_id, artifact_hashes, audit_trail, kill_switch_hooked, tampered, passed, evidence_ref).
- [x] _RemediationContext (ExecutionContext protocol for T068 hook).
- [x] RemediationIntegrityGate.check (fail-closed: tampered OR missing audit -> reject).
- [x] RemediationIntegrityGate.hook_kill_switch (register context, T068).
- [x] RemediationIntegrityGate.should_halt (query T068 halt).
- [x] RemediationIntegrityGate.issue_halt (emergency stop, T068).
- [x] RemediationIntegrityGate._record_evidence (T001 provenance via EvidenceStore).
- [x] RemediationIntegrityGate.provenance_complete / result_hash.
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Integrity (T078) + Kill Switch (T068) + Remediation (T094-T097) (import-level).
