# TASK-070 Implementation

Real implementation lives in the `aios/security/` package (extended in place):

| Module | Public API | Responsibility |
|--------|-----------|----------------|
| `aios/security/context.py` | `SecurityContext` | Identity + authz state; `secret_refs` only (no values). |
| `aios/security/auth.py` | `AuthValidator`, `TokenRecord`, `AuthError` | External-entry auth, fail-closed. |
| `aios/security/secrets.py` | `SecretStore`, `SecretRef`, `redact_message`, `SecretError` | Scoped secret refs + log redaction. |
| `aios/security/audit.py` | `SecurityAudit`, `AuditRecord` | Privileged-action audit evidence (provenance). |
| `aios/security/broker.py` | `SecurityPermissionBroker` | Wrap Runtime `PermissionBroker` + `PolicyEngine`. |
| `aios/security/engine.py` | `SecurityBaseline`, `SecurityDecision` | Auth→permission→scope→governor→audit (deterministic, fail-closed). |
| `aios/security/api_bridge.py` | `from_api_context` | Convert `aios.api.auth.AuthContext` → `SecurityContext` (lazy import). |

Tests: `aios/security/tests/test_security_baseline.py`
Run: `python -m pytest aios/security -q`

This directory is a pointer only — no source code is duplicated here.
