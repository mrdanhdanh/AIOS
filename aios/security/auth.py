"""Authentication for external entry (API/SDK) — TASK-070.

A minimal, deterministic identity/token validator for external callers. It is
**fail-closed**: a call without a valid token (missing / unknown / expired) is
rejected. It never defaults to allow.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from aios.security.context import SecurityContext


class AuthError(Exception):
    """Raised when authentication fails (fail-closed)."""


@dataclass
class TokenRecord:
    """A registered authentication token and the identity it maps to."""

    subject: str
    scopes: List[str] = field(default_factory=list)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    secret_refs: Dict[str, str] = field(default_factory=dict)
    expires_at: float = 0.0  # 0 == never expires


class AuthValidator:
    """Validates identity/token for external entry points.

    Integration note: this is the security-baseline counterpart to
    ``aios.api.auth.authenticate``. The API boundary can build a
    :class:`SecurityContext` from its own :class:`~aios.api.auth.AuthContext`
    via :func:`aios.security.api_bridge.from_api_context`.
    """

    def __init__(self) -> None:
        self._tokens: Dict[str, TokenRecord] = {}

    def register_token(self, token: str, record: TokenRecord) -> None:
        self._tokens[token] = record

    def _hash(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def validate(self, token: Optional[str]) -> SecurityContext:
        """Return an authenticated :class:`SecurityContext` or raise.

        Fail-closed: missing / unknown / expired tokens raise :class:`AuthError`.
        """
        if not token:
            raise AuthError("missing authentication token")
        rec = self._tokens.get(token)
        if rec is None:
            raise AuthError("invalid authentication token")
        if rec.expires_at and time.time() > rec.expires_at:
            raise AuthError("expired authentication token")
        return SecurityContext(
            principal=rec.subject,
            scopes=list(rec.scopes),
            permissions={k: list(v) for k, v in rec.permissions.items()},
            secret_refs=dict(rec.secret_refs),
            authenticated=True,
        )
