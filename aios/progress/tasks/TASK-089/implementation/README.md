# TASK-089 Implementation

Behavioral Conformance implementation lives in `aios/behavioral/`:

- `aios/behavioral/behavioral.py` — `BehaviorScenario`, `BehaviorHarness`,
  `BehaviorConformanceChecker`, `BehaviorConformanceResult`.
- `aios/behavioral/tests/test_behavioral.py` — 9 conformance tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.harness.verification` (VerificationPipeline, ReplayEngine, Verdict) — T030/T032
- `aios.governance.evidence.store` (EvidenceStore, Evidence) — T001 Rule 5
- `aios.conformance.conformance` (ConformanceReport, ConformanceRunner) — T087
