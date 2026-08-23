# TASK-018 Implementation — Dashboard SPA

Implementation lives in `aios/dashboard/` (M3 Desktop Edition — Dashboard).

> **Scope revision (audit 2026-08-22):** The canonical `docs/detailtask/T017-019.md` requires a React+Vite SPA, but the agreed task-folder `spec.md` revises scope to a **Python backend/data-layer service** (`aios/dashboard/`) that any frontend would consume. The React+Vite SPA is deferred; the backend contract is complete.

```
aios/dashboard/
  client.py              # REST API client (typed, contract-based)
  views.py               # 10 views: chat/workflow/timeline/tools/memory/artifacts/skills/models/prompts/health
  server.py              # Dashboard server (serves views via API)
  health.py              # Health view integration
  websocket_client.py    # WebSocket client (event stream, no bypass)
  mock_backend.py        # Mock backend for offline tests
  api_bridge.py          # API bridge (Dashboard ↔ FastAPI)
  observability_views.py # Observability views (metrics/audit/doctor)
  __init__.py            # re-exports
  tests/
    test_dashboard.py
    test_views.py
    test_client.py
```

All actions go through `aios/api` → `Orchestrator/Runtime/Policy` (no direct DB/Runtime/Tool access). State reflects real execution state.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
