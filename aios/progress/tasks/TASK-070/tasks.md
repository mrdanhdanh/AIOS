# TASK-070 — Breakdown

- [x] Step 1 — Định nghĩa `SecurityContext` (principal, scopes, permissions, secret_refs, evidence_ref) trong `aios/security/context.py`.
- [x] Step 2 — Auth validator `AuthValidator`/`TokenRecord` (fail-closed) trong `aios/security/auth.py`.
- [x] Step 3 — Secret handling `SecretStore`/`SecretRef` + `redact_message` trong `aios/security/secrets.py`.
- [x] Step 4 — Audit `SecurityAudit`/`AuditRecord` (dùng `governance.evidence` nếu có) trong `aios/security/audit.py`.
- [x] Step 5 — Permission broker integration `SecurityPermissionBroker` wrap Runtime Permission+Policy trong `aios/security/broker.py`.
- [x] Step 6 — Engine `SecurityBaseline`/`SecurityDecision` (auth→permission→scope→governor→audit, deterministic, fail-closed) trong `aios/security/engine.py`.
- [x] Step 7 — API bridge `from_api_context` (lazy import `aios.api.auth`) trong `aios/security/api_bridge.py`.
- [x] Step 8 — Export public API trong `aios/security/__init__.py`.
- [x] Step 9 — Tests phủ mọi AC + Test Matrix trong `aios/security/tests/test_security_baseline.py`.
- [x] Step 10 — Chạy `python -m pytest aios/security -q` → 27 passed.
- [x] Step 11 — Tạo 9 lifecycle artifacts dưới `aios/progress/tasks/TASK-070/`.
