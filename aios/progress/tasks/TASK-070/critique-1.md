# TASK-070 — Critique 1

## Strengths
- Tái sử dụng Runtime `PermissionBroker` + `PolicyEngine` (T054/Policy) thay vì
  xây hệ thống song song → tuân thủ "No parallel security system".
- `SecurityContext` chỉ giữ `secret_refs` (refs), không giữ value → không leak.
- Engine `check` fail-closed ở mọi cổng (auth → permission → scope → governor).
- Tích hợp Governor (T054) và API (`api_bridge` lazy import) rõ ràng.

## Risks / Gaps
- `PolicyEngine` mặc định trả `INSUFFICIENT` (không `ALLOW`) khi không có rule →
  cần xử lý: grant hợp lệ + không `DENY` → ALLOW.
- Governor `check_scope` đọc `self._scope`, không đọc `ctx.scope` → engine phải
  align scope của governor với `ctx.scopes` khi evaluate.
- Redaction regex phải giữ key, chỉ thay value → tránh giữ lại secret value.
- Import `aios.api.auth` kéo theo `fastapi` → phải lazy import để không phá
  import `aios.security` khi thiếu fastapi.

## Required revisions
- Sửa `SecurityPermissionBroker.check`: `result.decision != DENY` → ALLOW.
- Sửa `redact_message` patterns: group(1)=key, group(2)=value, thay value bằng
  `<REDACTED>`.
- Engine align governor `_scope` với `ctx.scopes` (có restore).
- `api_bridge.from_api_context` lazy import `aios.api.auth`.
