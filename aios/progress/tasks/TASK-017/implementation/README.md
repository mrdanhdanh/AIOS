# TASK-017 Implementation

Source files created for TASK-017 (FastAPI REST + WebSocket):

- `aios/api/__init__.py` — package re-exports
- `aios/api/app.py` — FastAPI factory, lifespan, middleware, OpenAPI
- `aios/api/schemas.py` — Pydantic v2 request/response schemas
- `aios/api/errors.py` — Error model, stable schema, no traceback
- `aios/api/auth.py` — Auth boundary (API key, Bearer)
- `aios/api/events.py` — EventService, EventEnvelope, whitelist
- `aios/api/contracts.py` — ApiVersion, version negotiation
- `aios/api/deps.py` — Shared router dependencies
- `aios/api/websocket.py` — ConnectionManager, WebSocketGateway
- `aios/api/routers/health.py` — Health endpoints
- `aios/api/routers/system.py` — System info/config
- `aios/api/routers/orchestrator.py` — Decision pipeline
- `aios/api/routers/executions.py` — Execution CRUD + policy
- `aios/api/routers/workflows.py` — Workflow CRUD + validation
- `aios/api/routers/tasks.py` — Task CRUD
- `aios/api/routers/agents.py` — Agent list/get
- `aios/api/routers/capabilities.py` — Capability CRUD
- `aios/api/routers/tools.py` — Tool CRUD
- `aios/api/routers/skills.py` — Skill CRUD + enable/disable
- `aios/api/routers/memory.py` — Memory CRUD + search
- `aios/api/routers/artifacts.py` — Artifact CRUD + content
- `aios/api/routers/models.py` — Model list/get (provider registry)
- `aios/api/routers/prompts.py` — Prompt CRUD + render
- `aios/api/routers/events.py` — Event publish/list/types
- `aios/api/tests/test_api.py` — 60 comprehensive offline tests
