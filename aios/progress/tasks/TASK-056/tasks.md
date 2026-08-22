# TASK-056 — Breakdown

## Steps
1. `aios/goal_durability/contracts.py` — DurableCheckpoint (full semantics + content_hash), InterruptionCause, ResumeVerdict.
2. `aios/goal_durability/layer.py` — GoalDurabilityLayer: checkpoint (atomic/monotonic), validate, detect_stale, idempotency guard, resume.
3. `aios/goal_durability/tests/test_goal_durability.py` — 9 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-056-01..10 PASS, gate PASS, no regressions.
