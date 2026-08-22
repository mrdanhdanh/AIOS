# Critique 2 — TASK-095

- Confirm `CandidateEngine.run` trả về `CandidatePlan` chỉ chứa candidate compliant
  (policy_violation → rejected list, fail-closed).
- `RiskScorer.score` deterministic: cùng candidate → cùng risk_score.
- `result_hash` dùng sha256 của JSON sort_keys → deterministic ranking hash.
- Integration import-level với Governor/Autonomy/Diagnosis, không rewrite dependency.
- Kết luận: implementation đủ điều kiện qua review.
