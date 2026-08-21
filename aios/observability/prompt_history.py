"""Prompt history recorder.

AC-021-03: Prompt history traceable.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptRecord:
    """Record of a prompt invocation."""

    prompt_id: str
    version: int
    timestamp: float
    template_hash: str = ""
    variables: dict[str, str] = field(default_factory=dict)
    execution_id: str = ""
    model_id: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    evaluation_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "version": self.version,
            "timestamp": self.timestamp,
            "template_hash": self.template_hash,
            "variables": self.variables,
            "execution_id": self.execution_id,
            "model_id": self.model_id,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "evaluation_score": self.evaluation_score,
        }


class PromptHistory:
    """Records prompt invocations for traceability.

    AC-021-03: Prompt history traceable.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: list[PromptRecord] = []

    def record(
        self,
        prompt_id: str,
        version: int,
        template_hash: str = "",
        variables: dict[str, str] | None = None,
        execution_id: str = "",
        model_id: str = "",
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        evaluation_score: float | None = None,
    ) -> PromptRecord:
        """Record a prompt invocation."""
        rec = PromptRecord(
            prompt_id=prompt_id,
            version=version,
            timestamp=time.time(),
            template_hash=template_hash,
            variables=variables or {},
            execution_id=execution_id,
            model_id=model_id,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            evaluation_score=evaluation_score,
        )
        with self._lock:
            self._records.append(rec)
        return rec

    def query(
        self,
        prompt_id: str | None = None,
        execution_id: str | None = None,
        limit: int | None = None,
    ) -> list[PromptRecord]:
        with self._lock:
            records = list(self._records)
        if prompt_id:
            records = [r for r in records if r.prompt_id == prompt_id]
        if execution_id:
            records = [r for r in records if r.execution_id == execution_id]
        if limit:
            records = records[-limit:]
        return records

    def count(self) -> int:
        with self._lock:
            return len(self._records)
