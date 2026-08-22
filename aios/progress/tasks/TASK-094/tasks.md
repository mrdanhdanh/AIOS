# Task Breakdown — TASK-094

- [x] SymptomSeverity enum (LOW/MEDIUM/HIGH/CRITICAL).
- [x] Symptom dataclass (symptom_id, description, evidence_ref, severity).
- [x] Incident dataclass (incident_id, kind, severity, signal, evidence_ref).
- [x] Diagnosis dataclass (incident_id, symptoms, root_cause, confidence, causal_trace, evidence_ref, escalated).
- [x] Diagnosis.is_traceable (fail-closed: non-traceable → escalated).
- [x] DetectDiagnoseEngine.observe (feed StuckDetector + MetricsCollector).
- [x] DetectDiagnoseEngine.detect (anomaly/failure/deviation → Incident).
- [x] DetectDiagnoseEngine.capture_symptom (evidence-backed).
- [x] DetectDiagnoseEngine.diagnose (fail-closed: thiếu evidence/trace → escalate).
- [x] DetectDiagnoseEngine._record_evidence (T001 provenance via EvidenceStore).
- [x] DetectDiagnoseEngine.provenance_complete / result_hash.
- [x] Tests 9 cases (Test Matrix).
- [x] Tích hợp Stuck (T061) + Observability (T065/T069) + Evidence (T001) (import-level).
