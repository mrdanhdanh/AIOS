"""Evaluation Collector — gathers evaluation data post-execution.

AC-022-03: Evaluation collected after execution.
AC-022-04: Evaluation has provenance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationRecord:
    """Evaluation data for a single execution."""

    execution_id: str
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    quality_score: float = 0.0
    latency_ms: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    tools_used: list[str] = field(default_factory=list)
    policy_violations: int = 0
    provenance: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "success": self.success,
            "quality_score": self.quality_score,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "tools_used": self.tools_used,
            "policy_violations": self.policy_violations,
            "provenance": self.provenance,
            "metadata": self.metadata,
        }


class EvaluationCollector:
    """Collects evaluation data after execution.

    AC-022-03: Evaluation collected after execution.
    AC-022-04: Evaluation has provenance.
    """

    def __init__(self) -> None:
        self._records: list[EvaluationRecord] = []

    def collect(
        self,
        execution_id: str,
        success: bool = True,
        quality_score: float = 0.0,
        latency_ms: float = 0.0,
        tokens_used: int = 0,
        cost: float = 0.0,
        tools_used: list[str] | None = None,
        policy_violations: int = 0,
        provenance: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvaluationRecord:
        """Collect evaluation data for an execution."""
        record = EvaluationRecord(
            execution_id=execution_id,
            success=success,
            quality_score=quality_score,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            cost=cost,
            tools_used=tools_used or [],
            policy_violations=policy_violations,
            provenance=provenance or [f"exec:{execution_id}"],
            metadata=metadata or {},
        )
        self._records.append(record)
        return record

    def get_record(self, execution_id: str) -> EvaluationRecord | None:
        for r in self._records:
            if r.execution_id == execution_id:
                return r
        return None

    def list_records(self) -> list[EvaluationRecord]:
        return list(self._records)

    def avg_quality(self) -> float:
        if not self._records:
            return 0.0
        return sum(r.quality_score for r in self._records) / len(self._records)

    def total_cost(self) -> float:
        return sum(r.cost for r in self._records)

    def total_tokens(self) -> int:
        return sum(r.tokens_used for r in self._records)
