# TASK-072 — Regression

## Dependency closure
- TASK-054 Autonomy Governor — thêm `state()` (read-only, backward-compatible). Tests governor không break.
- TASK-070 Security Baseline — reuse `AuthValidator` + `SecretStore`/`redact_message` (không đổi).
- `aios/observability`, `aios/core/healthcheck`, `aios/governance/evidence` — chỉ đọc, không đổi.
- `aios/api` — bridge lazy import, không đổi `create_app`.

## Regression result
- Re-run: `python -m pytest aios/dashboard -q` → **140 passed** (130 existing + 10 new).
- Không break bất kỳ test dashboard hiện có.

## Status
- REGRESSION gate: PASS.
