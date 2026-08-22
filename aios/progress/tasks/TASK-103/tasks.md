# Task Breakdown — TASK-103

- [x] ConstitutionDecision dataclass (decision_id, principal, action, policy_ref, risk, trust_remaining, halt_active, evidence_ref).
- [x] AuditEntry dataclass (decision_id, principal, action, policy_ref, constitution_compliant, prev_entry_hash, timestamp, evidence_ref) + canonical/content_hash.
- [x] AutonomyConstitution (supreme rules R1-R4, is_compliant fail-closed).
- [x] AuditTrail.append (hash-chained) / verify_chain / detect_tamper (T078).
- [x] ConstitutionEngine.is_blocked / evaluate (fail-closed BLOCK + audit).
- [x] ConstitutionEngine.evaluate_with_trust (T102 binding).
- [x] ConstitutionEngine._record_evidence (T001 provenance).
- [x] ConstitutionEngine.provenance_complete / result_hash.
- [x] CONSTITUTION.md (ADR, supreme rules).
- [x] Tests 6 cases (Test Matrix).
- [x] Tích hợp Autonomy Safety + Trust + Evidence + Integrity + Kill Switch (import-level).
