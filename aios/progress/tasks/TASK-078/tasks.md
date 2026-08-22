# Task Breakdown — TASK-078

- [x] IntegrityReport dataclass (evidence_id, content_hash, verifier_version, config_hash, tampered, verdict_class, promoted_to_pass, provenance_complete).
- [x] VerifierLock (version + config_hash, lock per run).
- [x] IntegrityChecker.verify_evidence_hash / is_tampered.
- [x] IntegrityChecker.lock_verifier / verifier_changed.
- [x] IntegrityChecker.promotes_to_pass (fail-closed).
- [x] IntegrityChecker.provenance_complete.
- [x] IntegrityChecker.evaluate (combined fail-closed report).
- [x] Tests 8 cases (Test Matrix).
- [x] Tích hợp Harness + Evidence (import-only, no rewrite).
