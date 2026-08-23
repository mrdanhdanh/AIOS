# TASK-221 — Breakdown

1. **Schema** (`aios/api/schemas.py`): `CoordinatorRunRequest`, `CoordinatorRunResponse`, `CoordinatorStep`.
2. **Router** (`aios/api/routers/coordinator.py`): `POST /run`, `GET /{task_id}`; in-memory store; gọi `CoordinatorAgent`.
3. **App** (`aios/api/app.py`): include `coordinator_router` với `API_PREFIX`.
4. **Tests** (`aios/api/tests/test_coordinator_router.py`): POST + GET.
5. **Evidence/docs**: artifacts + PLAN/LOG/STATS.
6. **Governance**: `gate_check.py --task TASK-221` + `pytest aios -q` → commit.
