# TASK-095 Implementation

Candidate Generation + Risk Scoring implementation lives in `aios/remediation_candidate/`:

- `aios/remediation_candidate/candidate.py` — `Candidate`, `CandidatePlan`,
  `CandidateGenerator`, `RiskScorer`, `PolicyFilter`, `CandidateRanker`, `CandidateEngine`.
- `aios/remediation_candidate/tests/test_candidate.py` — 7 candidate/risk tests (Test Matrix).

Integration (import-level, no rewrite):
- `aios.autonomy_governor` (AutonomyGovernor, AutonomyAction, AutonomyPolicy, ActionContext) — T054/T067
- `aios.remediation_detect` (Diagnosis) — T094
- `aios.governance.evidence.store` (EvidenceStore) — T001 Rule 5
