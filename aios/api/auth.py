"""Auth boundary — minimal for M3 (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .errors import ApiError, ErrorCode

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthConfig:
    enabled: bool = False
    api_keys: Dict[str, str] = field(default_factory=dict)
    allow_anonymous: bool = True
    default_subject: str = "anonymous"


@dataclass
class AuthContext:
    subject: str
    authenticated: bool = False
    token_hash: str = ""

    @property
    def is_anonymous(self) -> bool:
        return not self.authenticated


_auth_config = AuthConfig()


def configure_auth(config: AuthConfig) -> None:
    global _auth_config
    _auth_config = config


async def authenticate(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> AuthContext:
    cfg = _auth_config
    if x_api_key is not None:
        subject = cfg.api_keys.get(x_api_key)
        if subject is not None:
            return AuthContext(subject=subject, authenticated=True, token_hash=hashlib.sha256(x_api_key.encode()).hexdigest()[:16])
        if cfg.enabled and not cfg.allow_anonymous:
            raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid API key")
    if credentials is not None and credentials.credentials:
        subject = cfg.api_keys.get(credentials.credentials)
        if subject is not None:
            return AuthContext(subject=subject, authenticated=True)
        if cfg.enabled and not cfg.allow_anonymous:
            raise ApiError(ErrorCode.UNAUTHORIZED, "Invalid bearer token")
    if cfg.enabled and not cfg.allow_anonymous:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Authentication required")
    return AuthContext(subject=cfg.default_subject, authenticated=False)


async def require_auth(auth: AuthContext = Depends(authenticate)) -> AuthContext:
    if auth.is_anonymous and _auth_config.enabled and not _auth_config.allow_anonymous:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Authentication required")
    return auth
