# TASK-235 — Breakdown

## Sub-tasks
1. **T235.1** — `detect_conflicts()` (cùng requirement, status mâu thuẫn, loại UNKNOWN/STALE).
2. **T235.2** — `replay(run_id)` + `quality_score(producer_trust)`.
3. **T235.3** — `is_valid_for_evaluation()` (từ chối UNKNOWN/STALE/conflict).
4. **T235.4** — Test + architecture gate.

## Verification
`pytest aios/governance/evidence/tests/test_evidence.py -k "conflict or replay or quality"` + `pytest aios/governance/architecture`.
