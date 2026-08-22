# TASK-072 — Critique 1

## Strengths
- Rõ ràng: observability UI, không control plane → tránh song song control plane.
- Tái dùng `aios.security.auth` (fail-closed) và `aios.security.secrets` (redact) thay vì tự viết.
- Dependency injection cho sources → dễ test, deterministic.

## Risks / Gaps
- GOALS / ALERTS không có module chuyên biệt trong danh sách tích hợp → cần `ReadOnlySource` protocol + default empty để không phá architecture.
- `AutonomyGovernor` không có public read accessor → cần thêm `state()` (backward-compatible).
- `MetricsCollector.snapshot()` có `timestamp` không deterministic → phải loại bỏ khỏi render.
- `aios.api` import fastapi → phải lazy import trong bridge để không phá import dashboard.

## Required revisions
- Đảm bảo mọi item mang `evidence_ref` + `provenance` (kể cả health/autonomy).
- `render()` phải deep-copy + redact để caller không mutate source và secret không lọt.
- `build_view` gọi `require_auth` trước khi dựng data (fail-closed auth).
