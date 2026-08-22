# TASK-096 Implementation

Simulation + Meta-Verification Gate implementation lives in `aios/remediation_simulation/`:

- `aios/remediation_simulation/simulation.py` — `Sandbox`, `SimulationEngine`,
  `SimulationGate`, `SimulationGateEngine`, `SimulationResult`.
- `aios/remediation_simulation/tests/test_simulation.py` — 7 simulation/meta tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.harness.verification` (VerificationPipeline, Verdict) — T030/T032
- `aios.meta_harness` (MetaHarness, MetaVerdict) — T091
- `aios.remediation_candidate` (Candidate) — T095
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
