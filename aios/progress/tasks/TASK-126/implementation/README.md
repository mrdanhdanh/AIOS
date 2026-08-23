# TASK-126 Implementation

Coding Planner + PlanVerifier lives in:

- `aios/coder/planner.py` — `CodingPlanner`, `PlanVerifier`, `CodingPlan`, `CodingStep`, `PlanStatus`, `PlanVerifyError`.
- Tests trong `aios/coder/tests/test_planner.py` (9 tests, Test Matrix TASK-126).

Design:
- `CodingPlanner.plan()` — deterministic-first: known intent (`_KNOWN_INTENTS`) → rule-based steps, `llm_call_count=0` (T001 Rule 4). Unknown intent → optional `llm_fallback` (counted). Same (request, rules) → same `content_hash` (deterministic).
- `PlanVerifier.verify()` — fail-closed (T078): requires ≥1 mutating action (create/patch/refactor) + ≥1 test action; valid target; `policy_ok` (T113). On failure → `PlanVerifyError`, `status=REJECTED`.
- Mọi plan ghi `evidence_id` + `content_hash` (sha256) → provenance (T001 Rule 5).

Integration (import-level, no rewrite):
- `aios.coder.contract` (T125) — agent_ref boundary
- `aios.governance.evidence` (T001) — provenance schema
- `aios.governance.architecture` (ARCH) — layer classification (unknown)
- `aios.coder.planner` (T126) -> `aios.coder.generation` (T127) / `aios.coder.patch` (T128)
