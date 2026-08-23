# TASK-221 — Coordinator Chat API Endpoint

## Objective
Thêm endpoint REST cho phép client (chat UI / script) gửi `{task_id, objective, scope, deliverables, acceptance, dependencies}` và nhận kết quả điều phối từ `CoordinatorAgent` (TASK-220). Endpoint nằm trong tầng `api`, gọi xuống `agents` (downward-only, ARCH-004), không tự thực thi logic governance.

## Scope
**In scope:**
- `aios/api/routers/coordinator.py` — `POST /coordinator/run` + `GET /coordinator/{task_id}`.
- `aios/api/schemas.py` — `CoordinatorRunRequest`, `CoordinatorRunResponse`.
- `aios/api/app.py` — include router mới.
- `aios/api/tests/test_coordinator_router.py` — test endpoint.
- Task artifacts + evidence.

**Out of scope:** auth sâu, streaming websocket, persistence của artifact (chỉ trả về in-memory result).

## Deliverables
- Router `coordinator.py` với 2 endpoints, dùng `CoordinatorAgent` + `SpecWriter`/`Critic`/`Reviewer` + fake `Orchestrator` (hoặc thật nếu có lifecycle sẵn).
- Schema request/response Pydantic v2, version `API_VERSION`.
- Include router vào `create_app` (prefix `API_PREFIX`).
- Test: POST trả `approved`/`closed`/`artifacts`/`steps`; GET trả status.
- Cập nhật PLAN/LOG/STATS + commit `TASK-221: ... — DONE`.

## Acceptance Criteria
- `POST /api/v1/coordinator/run` nhận `CoordinatorRunRequest` → trả `CoordinatorRunResponse` (task_id, approved, closed, artifacts keys, steps).
- Endpoint gọi `CoordinatorAgent.coordinate()` thực tế (không mock cứng).
- `GET /api/v1/coordinator/{task_id}` trả về kết quả đã lưu (in-memory store) hoặc 404 nếu chưa có.
- Architecture gate: `api` layer import `aios.agents` (allowed downward) — không vi phạm ARCH-001..004.
- `python -m pytest aios/api/tests/test_coordinator_router.py -q` → passed.
- Full suite regression green.

## Dependencies
- TASK-220 (CoordinatorAgent), TASK-017 (API boundary), TASK-001 (lifecycle/gates).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `api` → `agents` (downward OK). Cấm `subprocess`/`os` (ARCH-001).
- Quy tắc 8: DONE → commit + update PLAN/LOG/STATS.
