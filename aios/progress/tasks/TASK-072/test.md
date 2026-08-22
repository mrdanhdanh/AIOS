# TASK-072 — Test

## How to run
```
python -m pytest aios/dashboard -q
```

## What is covered
- **Unit / Contract** (`test_observability_views.py`):
  - HEALTH view aggregates probes correctly (AC1).
  - Read-only: `mutate_state` / `apply_action` raise `ReadOnlyViolation` (AC2).
  - Auth required: missing/invalid token → `DashboardAuthError` (AC3).
  - Evidence view resolves full provenance chain (AC4).
  - No secret leak: `api_key=...` and known secret values redacted (AC5).
  - Deterministic: `render_all` identical for same sources; deep-copy isolation (AC6).
  - AUTONOMY view projects `AutonomyGovernor.state()` (AC7).
- **Integration** (`test_api_bridge.py`):
  - FastAPI router blocks unauthenticated (401), serves authed view (200), accepts Bearer/X-API-Key, 404 on unknown view, lists 5 views (AC3/AC7).
- **Architecture**: dashboard imports only peer/downward modules (no `agents/`).
- **Regression**: existing 130 dashboard tests still PASS (not broken).
