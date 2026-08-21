"""Shared dependencies for API routers (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, Query, Request

from aios.runtime.kernel import RuntimeKernel

from .auth import AuthContext, authenticate
from .contracts import CURRENT_API_VERSION, negotiate_version
from .events import EventService
from .schemas import PaginationParams
from .websocket import WebSocketGateway


def get_kernel(request: Request) -> RuntimeKernel:
    return request.app.state.kernel


def get_event_service(request: Request) -> EventService:
    return request.app.state.event_service


def get_gateway(request: Request) -> WebSocketGateway:
    return request.app.state.gateway


def get_pagination(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def get_api_version(
    x_api_version: Optional[str] = Header(default=None, alias="X-API-Version"),
) -> str:
    try:
        return negotiate_version(x_api_version).version
    except ValueError:
        return CURRENT_API_VERSION


def get_auth(auth: AuthContext = Depends(authenticate)) -> AuthContext:
    return auth
