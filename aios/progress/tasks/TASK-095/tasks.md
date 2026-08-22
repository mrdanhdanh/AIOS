# Task Breakdown — TASK-095

- [x] Candidate dataclass (candidate_id, source_diagnosis_id, action, risk_score, policy_compliant, rollback_cost, blast_radius, impact, autonomy_action, evidence_ref).
- [x] CandidatePlan dataclass (source_diagnosis_id, candidates, rejected, evidence_ref).
- [x] CandidateGenerator.generate (từ Diagnosis → candidates, deterministic catalog).
- [x] RiskScorer.score (evidence-based: impact/rollback/blast-radius).
- [x] PolicyFilter.filter (T054/T067: vi phạm policy → rejected, fail-closed).
- [x] CandidateRanker.rank (low → high risk).
- [x] CandidateEngine.run (generate → score → filter → rank, fail-closed).
- [x] CandidateEngine._record_evidence (T001 provenance via EvidenceStore).
- [x] CandidateEngine.provenance_complete / result_hash.
- [x] Tests 7 cases (Test Matrix).
- [x] Tích hợp Diagnosis (T094) + Governor/Policy (T054) + Autonomy (T067) (import-level).
