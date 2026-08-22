# TASK-072 — Breakdown

- [x] Step 1 — Định nghĩa `DashboardView` / `DashboardViewType` (view, data_source, refresh, evidence_ref).
- [x] Step 2 — `ObservabilityDashboard` builder với dependency injection các read-only sources.
- [x] Step 3 — Read-only fail-closed: `mutate_state` / `apply_action` raise `ReadOnlyViolation`.
- [x] Step 4 — Auth required: `require_auth` reuse `aios.security.auth.AuthValidator` (fail-closed).
- [x] Step 5 — No secret leak: `_redact` reuse `aios.security.secrets`.
- [x] Step 6 — Evidence traceability: EVIDENCE view dựng provenance chain từ `EvidenceStore`.
- [x] Step 7 — Tích hợp `aios.core.healthcheck`, `aios.observability`, `aios.autonomy_governor` (thêm `state()`), `aios.governance.evidence`.
- [x] Step 8 — FastAPI bridge `api_bridge.py` mount view qua `aios.api` (lazy import).
- [x] Step 9 — Tests `test_observability_views.py` + `test_api_bridge.py`; chạy `pytest aios/dashboard` PASS.
- [x] Step 10 — 9 artifact governance trong `aios/progress/tasks/TASK-072/`.
