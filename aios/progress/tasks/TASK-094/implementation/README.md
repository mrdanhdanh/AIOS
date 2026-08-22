# TASK-094 Implementation

Detect + Diagnose implementation lives in `aios/remediation_detect/`:

- `aios/remediation_detect/detect.py` — `Symptom`, `Incident`, `Diagnosis`,
  `DetectDiagnoseEngine`.
- `aios/remediation_detect/tests/test_detect.py` — 9 detect/diagnose tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.stuck_detection` (StuckDetector, IterationSample) — T061
- `aios.observability` (MetricsCollector, AuditService) — T065/T069
- `aios.governance.evidence.store` (EvidenceStore, Evidence) — T001 Rule 5
