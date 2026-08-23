"""Shared fakes for execution subsystem tests (M20)."""

from __future__ import annotations

from aios.execution._common import _hash
from aios.execution.contract import ExecutionResponse, ExecutionStatus


class FakeDispatcher:
    """In-memory dispatcher returning a deterministic SUCCESS response."""

    def dispatch(self, request):
        return ExecutionResponse(
            request_id=request.request_id,
            status=ExecutionStatus.SUCCESS,
            exit_code=0,
            stdout_hash=_hash(request.command),
            stderr_hash=_hash(request.command + ":lint"),
        )


class FakeBlockedDispatcher:
    """Dispatcher that always returns a BLOCKED response (T078)."""

    def dispatch(self, request):
        return ExecutionResponse(
            request_id=request.request_id,
            status=ExecutionStatus.BLOCKED,
            exit_code=1,
            stdout_hash="",
            stderr_hash="",
        )
