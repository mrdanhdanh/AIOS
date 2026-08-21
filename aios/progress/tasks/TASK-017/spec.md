# TASK-017 — FastAPI REST + WebSocket

## Objective
Xây API boundary chính thức (REST + WebSocket) để Dashboard, VS Code Extension và CLI có thể sử dụng cùng một Runtime/Orchestrator backend. API là presentation layer, không chứa business logic, không bypass Policy/Permission.

## Scope
- FastAPI app, REST routers (15 groups), WebSocket gateway, schemas (Pydantic v2), error model, auth boundary, event service, versioning.

## Deliverables
- `aios/api/` package: app, schemas, errors, auth, events, contracts, deps, websocket, 15 routers, tests.

## Acceptance Criteria
1. Shared contracts via OpenAPI (versioned, `/api/v1`)
2. REST não bypass Policy (DENY → 403)
3. WebSocket whitelist events only, no execution bypass
4. Execution state = StateStore (authoritative)
5. Stable error schema `{code, message, details, request_id}`, no traceback
6. API versioning via `/api/v1` + `X-API-Version` header
7. No implementation detail exposed
8. WebSocket reconnect via `last_event_id` replay
9. Offline tests (no LLM, no network)
10. `api` layer import guard correct (no reverse imports)
11. OpenAPI spec auto-generated for all routers
12. Full regression PASS

## Dependencies
TASK-010, 011, 012, 013, 014, 015, 016 (all DONE)

## Governance references
Rule 3, 4, 5, 7
