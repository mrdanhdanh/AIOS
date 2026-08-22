"""Bridge between the API auth boundary and the security baseline (TASK-070).

Converts an :class:`~aios.api.auth.AuthContext` (produced by the FastAPI
boundary) into a :class:`~aios.security.context.SecurityContext` that the
security baseline can reason about. The ``aios.api.auth`` import is performed
lazily so that ``aios.security`` does not hard-depend on FastAPI at import time.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from aios.security.context import SecurityContext


def from_api_context(
    auth_ctx: Any,
    scopes: Optional[List[str]] = None,
    permissions: Optional[Dict[str, List[str]]] = None,
    secret_refs: Optional[Dict[str, str]] = None,
    evidence_ref: Optional[str] = None,
) -> SecurityContext:
    """Build a :class:`SecurityContext` from an API ``AuthContext``.

    Raises ``TypeError`` if ``auth_ctx`` is not an API ``AuthContext``.
    """
    from aios.api.auth import AuthContext  # lazy: FastAPI dependency

    if not isinstance(auth_ctx, AuthContext):
        raise TypeError("auth_ctx must be an aios.api.auth.AuthContext")
    return SecurityContext(
        principal=auth_ctx.subject,
        scopes=list(scopes or []),
        permissions={k: list(v) for k, v in (permissions or {}).items()},
        secret_refs=dict(secret_refs or {}),
        evidence_ref=evidence_ref,
        authenticated=auth_ctx.authenticated,
    )
