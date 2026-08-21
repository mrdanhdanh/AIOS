# TASK-018 — Dashboard SPA

## Objective
Build a unified operational dashboard as a Python backend service that provides data aggregation, API client, WebSocket client, and mock backend for 10 dashboard views. The dashboard serves as the data layer for any frontend (React, Vue, or terminal), reflecting true backend state through the existing FastAPI API boundary.

## Scope
### In scope
- Dashboard server (Python backend data aggregation layer)
- API client for all 15 existing API endpoints
- WebSocket client for realtime event streaming
- Mock backend for offline/simulation mode
- 10 view models: Chat, Workflow, Timeline, Tools, Memory, Artifacts, Skills, Models, Prompts, Health
- State management (server state vs realtime state vs local UI state)
- Health status normalization (PASS/WARNING/ERROR/UNKNOWN)
- Policy feedback integration
- Artifact provenance tracing

### Out of scope
- Frontend SPA (React/Vue/HTML) — only Python data layer
- Mobile application
- User authentication UI (M7 scope)
- Multi-tenant dashboard views (M7 scope)

## Deliverables
- `aios/dashboard/__init__.py` — public API
- `aios/dashboard/server.py` — dashboard data aggregation server
- `aios/dashboard/client.py` — API client wrapper
- `aios/dashboard/websocket_client.py` — WebSocket event client
- `aios/dashboard/mock_backend.py` — offline mock backend
- `aios/dashboard/views.py` — 10 view models
- `aios/dashboard/health.py` — health status normalization
- `aios/dashboard/tests/` — comprehensive tests

## Acceptance Criteria
- AC-018-01: 10 views operational (Chat, Workflow, Timeline, Tools, Memory, Artifacts, Skills, Models, Prompts, Health)
- AC-018-02: UI data reflects true backend state (single source of truth in Runtime)
- AC-018-03: Realtime events via WebSocket update correctly
- AC-018-04: Reload loses no authoritative execution state
- AC-018-05: All actions go through API only
- AC-018-06: No business logic orchestration in dashboard layer
- AC-018-07: Policy-denied actions show clear reason
- AC-018-08: Artifact provenance traceable
- AC-018-09: Health UNKNOWN not displayed as healthy
- AC-018-10: Dashboard runs offline with Mock backend

## Dependencies
- TASK-017 (FastAPI REST + WebSocket)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
