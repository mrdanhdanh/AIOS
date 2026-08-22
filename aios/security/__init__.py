"""Security + Isolation (M7 — TASK-040) and Security Baseline (M10 — TASK-070).

TASK-070 extends this package with the security baseline 1.0: authentication,
authorization (via the Runtime PermissionBroker + PolicyEngine), least-privilege
scoping, secret handling, and audit. It integrates with ``aios.runtime``,
``aios.autonomy_governor`` and ``aios.api`` — it does NOT build a parallel
security system.
"""
from aios.security.contracts import Credential, NetworkPolicy, SandboxConfig
from aios.security.isolation import IsolationManager
from aios.security.context import SecurityContext
from aios.security.auth import AuthError, AuthValidator, TokenRecord
from aios.security.secrets import SecretError, SecretRef, SecretStore, redact_message
from aios.security.audit import AuditRecord, SecurityAudit
from aios.security.broker import SecurityPermissionBroker
from aios.security.engine import SecurityBaseline, SecurityDecision
from aios.security.api_bridge import from_api_context

__all__ = [
    # M7 — isolation
    "Credential",
    "NetworkPolicy",
    "SandboxConfig",
    "IsolationManager",
    # M10 — security baseline
    "SecurityContext",
    "AuthError",
    "AuthValidator",
    "TokenRecord",
    "SecretError",
    "SecretRef",
    "SecretStore",
    "redact_message",
    "AuditRecord",
    "SecurityAudit",
    "SecurityPermissionBroker",
    "SecurityBaseline",
    "SecurityDecision",
    "from_api_context",
]
