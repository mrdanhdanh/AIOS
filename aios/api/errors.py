"""API error model — stable schema, no traceback (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    POLICY_DENIED = "POLICY_DENIED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    CONTRACT_INVALID = "CONTRACT_INVALID"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


_CODE_STATUS = {
    ErrorCode.INVALID_REQUEST: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.POLICY_DENIED: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.CONTRACT_INVALID: 422,
    ErrorCode.RESOURCE_LIMIT: 429,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
}


class ApiError(Exception):
    def __init__(self, code: ErrorCode | str, message: str, *, status_code: int | None = None,
                 details: Dict[str, Any] | None = None, request_id: str | None = None) -> None:
        super().__init__(message)
        if isinstance(code, str):
            try:
                code = ErrorCode(code)
            except ValueError:
                code = ErrorCode.INTERNAL_ERROR
        self.code = code
        self.message = message
        self.details = details
        self.request_id = request_id or f"req-{uuid.uuid4().hex[:12]}"
        self.status_code = status_code or _CODE_STATUS.get(code, 500)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"code": self.code.value, "message": self.message, "request_id": self.request_id}
        if self.details is not None:
            d["details"] = self.details
        return d


def register_exception_handlers(app) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, exc: ApiError):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException):
        code = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.INVALID_REQUEST
        if exc.status_code == 401: code = ErrorCode.UNAUTHORIZED
        elif exc.status_code == 403: code = ErrorCode.POLICY_DENIED
        elif exc.status_code == 429: code = ErrorCode.RESOURCE_LIMIT
        elif exc.status_code >= 500: code = ErrorCode.INTERNAL_ERROR
        return JSONResponse(status_code=exc.status_code, content={
            "code": code.value, "message": str(exc.detail) if exc.detail else code.value,
            "request_id": f"req-{uuid.uuid4().hex[:12]}"})

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={
            "code": ErrorCode.CONTRACT_INVALID.value, "message": "Request validation failed",
            "details": {"errors": exc.errors()}, "request_id": f"req-{uuid.uuid4().hex[:12]}"})

    @app.exception_handler(Exception)
    async def _generic(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={
            "code": ErrorCode.INTERNAL_ERROR.value, "message": "Internal server error",
            "request_id": f"req-{uuid.uuid4().hex[:12]}"})
