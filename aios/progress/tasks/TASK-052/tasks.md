# TASK-052 — Breakdown

## Steps
1. `aios/world_model/contracts.py` — WorldState/Entity/Relation/Observation/Transition/Snapshot.
2. `aios/world_model/engine.py` — WorldModel.observe (validate→resolve→transition→commit), add_relation, snapshot, diff.
3. `aios/world_model/tests/test_world_model.py` — 8 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-052-01..07 PASS, gate PASS, no regressions.
