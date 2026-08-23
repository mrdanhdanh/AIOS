# Breakdown — TASK-126

1. `aios/coder/planner.py` — `CodingPlanner` (deterministic-first, rule table `_KNOWN_INTENTS`).
2. `CodingPlan` / `CodingStep` dataclasses (agent_ref, steps, llm_call_count, evidence_id, content_hash).
3. `PlanVerifier` fail-closed: yêu cầu ≥1 mutating action + ≥1 test action; target hợp lệ; policy_ok (T078/T113).
4. Deterministic path: rule đủ → `llm_call_count = 0` (T001 Rule 4); rule thiếu → `llm_fallback` (optional) + count.
5. Provenance: mọi plan có `evidence_id` + `content_hash` (T001 Rule 5).
6. Tests (9) theo Test Matrix TASK-126 + architecture guard.
7. Tích hợp: T125 -> T126 -> T127/T128 (M19).
