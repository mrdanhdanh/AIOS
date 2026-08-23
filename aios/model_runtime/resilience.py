"""Retry / Timeout / Streaming / Cancellation (TASK-114, M17).

Execution resilience for inference (T112) — bounded retry, timeout bound
(fail-closed), streaming chunks with provenance, and safe cancellation that
releases resources (T005). Deterministic: same config + same failure -> same
behavior. No infinite loops (T005).

Layering: ``unknown`` (infra) layer.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterator, Optional


__all__ = [
    "ResilienceError",
    "ResilienceConfig",
    "CancellationToken",
    "StreamChunk",
    "ResilienceManager",
]


class ResilienceError(Exception):
    """Raised when resilience bounds are exceeded (fail-closed, T078)."""


class ResilienceStatus(str, Enum):
    SUCCESS = "success"
    RETRY_EXHAUSTED = "retry_exhausted"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ResilienceConfig:
    """Resilience policy for an inference call."""

    max_retries: int = 0
    retry_cooldown: float = 0.0
    timeout_ms: float = 30_000.0
    streaming: bool = False
    cancellable: bool = True
    inference_ref: str = ""
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "retry_cooldown": self.retry_cooldown,
            "timeout_ms": self.timeout_ms,
            "streaming": self.streaming,
            "cancellable": self.cancellable,
            "inference_ref": self.inference_ref,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class StreamChunk:
    """A streamed chunk carrying provenance (T001 Rule 5)."""

    index: int
    content: str
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "content": self.content, "provenance": self.provenance}


class CancellationToken:
    """A thread-safe cancellation token that releases resources on cancel."""

    def __init__(self) -> None:
        self._cancelled = False
        self._lock = threading.Lock()
        self._released = False

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True

    def is_cancelled(self) -> bool:
        with self._lock:
            return self._cancelled

    def release(self) -> None:
        """Release any held resources (idempotent)."""
        with self._lock:
            self._released = True

    @property
    def released(self) -> bool:
        with self._lock:
            return self._released


class ResilienceManager:
    """Applies retry/timeout/streaming/cancellation to an inference call."""

    def __init__(self, *, producer: str = "model_runtime.resilience") -> None:
        self._producer = producer

    # -- bounded retry + timeout (fail-closed) ----------------------------- #
    def execute(
        self,
        config: ResilienceConfig,
        func: Callable[..., Any],
        *args: Any,
        token: Optional[CancellationToken] = None,
        **kwargs: Any,
    ) -> Any:
        """Execute ``func`` with bounded retry + timeout. Fail-closed."""
        deadline = time.monotonic() + config.timeout_ms / 1000.0
        attempts = 0
        max_attempts = config.max_retries + 1
        last_exc: Optional[Exception] = None
        while attempts < max_attempts:
            if token is not None and token.is_cancelled():
                if token is not None:
                    token.release()
                raise ResilienceError("cancelled before attempt")
            if time.monotonic() > deadline:
                if token is not None:
                    token.release()
                raise ResilienceError("timeout exceeded (fail-closed)")
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 — bounded retry
                last_exc = exc
                attempts += 1
                if attempts >= max_attempts:
                    break
                if config.retry_cooldown > 0:
                    time.sleep(config.retry_cooldown)
        if token is not None:
            token.release()
        raise ResilienceError(
            f"retry exhausted after {attempts} attempt(s): {last_exc}"
        )

    # -- streaming (chunk provenance) -------------------------------------- #
    def stream(
        self,
        config: ResilienceConfig,
        chunks: list[str],
        *,
        token: Optional[CancellationToken] = None,
        run_id: str = "stream",
    ) -> Iterator[StreamChunk]:
        """Yield streamed chunks, each with provenance (T001 Rule 5)."""
        for i, content in enumerate(chunks):
            if token is not None and token.is_cancelled():
                token.release()
                return
            yield StreamChunk(
                index=i,
                content=content,
                provenance=(
                    f"{self._producer}:chunk-{i}:{run_id}:"
                    f"{datetime.now(timezone.utc).isoformat()}"
                ),
            )
        if token is not None:
            token.release()

    # -- cancellation (safe resource release) ------------------------------ #
    @staticmethod
    def cancel(token: CancellationToken) -> None:
        token.cancel()
        # Resource release is performed by the executing path on cancel.
        token.release()
