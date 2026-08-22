# TASK-099 Implementation

Autonomous Harness Loop lives in `aios/autonomous_harness_loop/`:

- `aios/autonomous_harness_loop/loop.py` — `HarnessLoopRun`, `HarnessLoopEngine`.
- `aios/autonomous_harness_loop/tests/test_loop.py` — 6 loop tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.autonomous_scheduler` (Scheduler, ScheduleEntry, TriggerType) — T062
- `aios.harness.verification` (VerificationPipeline, Verdict) — T030/T032
- `aios.verification_integrity` (IntegrityChecker) — T078
- `aios.meta_harness` (MetaHarness, MetaVerdict) — T091
- `aios.remediation_detect` (DetectDiagnoseEngine, Incident, Diagnosis) — T094
- `aios.remediation_candidate` (CandidateEngine, Candidate) — T095
- `aios.remediation_simulation` (SimulationGateEngine, Sandbox) — T096
- `aios.remediation_apply` (ApplyOrchestrator, ApplyResult) — T097
- `aios.autonomy_governor` (AutonomyGovernor, AutonomyAction, AutonomyDecision, ActionContext) — T054/T067
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
