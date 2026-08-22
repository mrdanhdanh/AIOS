# TASK-072 — AIOS Dashboard 1.0

## Objective
Phát hành **Dashboard 1.0** — giao diện quan sát (observability) và vận hành AIOS: health, goals, autonomy state, evidence và alerts. TASK-072 là **observability UI, không phải control plane mới**, xây dựng trên `aios/dashboard` và `aios/observability`.

## Scope
**In scope**
- 5 view read-only: `HEALTH | GOALS | AUTONOMY | EVIDENCE | ALERTS`.
- `DashboardView` model (view, data_source read-only, refresh, evidence_ref).
- Read-only fail-closed: mọi action mutate qua dashboard → raise `ReadOnlyViolation`.
- Evidence traceability: mọi item mang `evidence_ref` + `provenance`.
- Auth required: truy cập không auth → BLOCK (reuse `aios.security.auth`).
- No secret leak: redact secret khỏi view data (reuse `aios.security.secrets`).
- Tích hợp `aios/observability`, `aios/api`, `aios/core/healthcheck`, `aios/autonomy_governor` (T054), `aios/governance/evidence` qua public import (peer/downward; không import `agents/`).
- FastAPI bridge (`aios/dashboard/api_bridge.py`) mount view qua `aios/api` với auth.

**Out of scope**
- Kill switch / mutate state (giữ cơ chế riêng T068).
- Parallel control plane.

## Deliverables
- `aios/dashboard/observability_views.py` — `DashboardView`, `DashboardViewType`, `ObservabilityDashboard`, `ReadOnlyViolation`, `DashboardAuthError`.
- `aios/dashboard/api_bridge.py` — `create_dashboard_router` / `register_dashboard_router` (FastAPI).
- Mở rộng `aios/autonomy_governor/governor.py` thêm `state()` (read-only accessor).
- Tests: `aios/dashboard/tests/test_observability_views.py`, `test_api_bridge.py`.
- 9 artifact trong `aios/progress/tasks/TASK-072/`.

## Acceptance Criteria
- AC1: Dashboard có view health/goals/autonomy/evidence/alerts.
- AC2: Dashboard read-only (không tự mutate state).
- AC3: Truy cập yêu cầu auth (T070).
- AC4: Mọi hiển thị trace được về evidence (provenance).
- AC5: Không hiển thị secret (T070).
- AC6: Cùng data source + view → cùng render (deterministic).
- AC7: Tích hợp được với Dashboard + Observability + API.
- AC8: Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- TASK-071 (DX) — done.
- TASK-054 (autonomy governor), TASK-070 (security baseline), governance/evidence, observability, core/healthcheck.

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`. Architecture: dashboard là peer module, chỉ import downward/peer (không `agents/`).
