# Task Breakdown — TASK-084

- [x] VersionPolicy dataclass (scheme, deprecation_window, baseline, adr_ref, evidence_ref).
- [x] ChangeType / VersionBump enums.
- [x] VersionChange / VersionDecision dataclasses.
- [x] VersionBaseline dataclass (ADR reference).
- [x] CompatibilityMatrix (1.0 ↔ 1.x, is_compatible / is_breaking).
- [x] VersionPolicyEngine.decide (fail-closed: breaking → MAJOR + ADR + deprecation).
- [x] VersionPolicyEngine.bump_version (deterministic SemVer bump).
- [x] VersionPolicyEngine.provenance_complete / baseline_hash.
- [x] Tests 9 cases (Test Matrix).
- [x] Tích hợp Contract (T064) + Migration (T074) (import-level).
