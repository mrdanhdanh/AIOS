# TASK-072 — Implementation

Real source code for Dashboard 1.0 lives under `aios/dashboard/` (NOT in this
folder — this is a pointer only, per governance convention).

## Modules
- `aios/dashboard/observability_views.py`
  - `DashboardViewType` (HEALTH|GOALS|AUTONOMY|EVIDENCE|ALERTS)
  - `DashboardView` (view, data_source, refresh, evidence_ref, items, summary)
  - `ObservabilityDashboard` — read-only builder; `build_view` / `render` / `render_all`
  - `ReadOnlyViolation` (fail-closed read-only), `DashboardAuthError` (fail-closed auth)
  - `require_auth` reuses `aios.security.auth.AuthValidator`
  - `_redact` reuses `aios.security.secrets` (redact_message + SecretStore.redact)
- `aios/dashboard/api_bridge.py`
  - `create_dashboard_router` / `register_dashboard_router` (FastAPI, lazy import)
- `aios/autonomy_governor/governor.py`
  - added `state()` read-only accessor for the AUTONOMY view

## Tests
- `aios/dashboard/tests/test_observability_views.py`
- `aios/dashboard/tests/test_api_bridge.py`

Run: `python -m pytest aios/dashboard -q`
