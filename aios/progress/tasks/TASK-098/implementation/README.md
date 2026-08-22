# TASK-098 Implementation

Remediation Integrity + Kill Switch implementation lives in `aios/remediation_integrity/`:

- `aios/remediation_integrity/integrity.py` — `RemediationArtifact`, `RemediationIntegrity`,
  `RemediationIntegrityGate`.
- `aios/remediation_integrity/tests/test_integrity.py` — 6 integrity/kill-switch tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.verification_integrity` (IntegrityChecker, sha256) — T078
- `aios.kill_switch` (KillSwitchController, HaltSignal, HaltScope, HaltSource) — T068
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
