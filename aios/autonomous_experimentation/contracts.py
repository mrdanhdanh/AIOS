"""Autonomous Experimentation contracts (TASK-058)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExperimentStatus(str, Enum):
    PROPOSED = "proposed"
    AUTHORIZED = "authorized"
    RUNNING = "running"
    EVALUATED = "evaluated"
    PROMOTION_READY = "promotion_ready"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass
class MetricSpec:
    """A single measurable metric for an experiment (not LLM-defined)."""
    name: str = ""
    direction: str = "increase"  # increase | decrease | maintain
    threshold: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "direction": self.direction, "threshold": self.threshold}


@dataclass
class Experiment:
    experiment_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    hypothesis: str = ""
    baseline_ref: str = ""
    baseline_version: str = ""  # immutable, resolved to a concrete version
    candidate_ref: str = ""
    candidate_version: str = ""  # immutable
    scenario_ref: str = ""
    metric_spec: list[MetricSpec] = field(default_factory=list)
    policy_scope: str = ""
    evidence_ref: str = ""
    evaluation_ref: str = ""
    status: ExperimentStatus = ExperimentStatus.PROPOSED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "hypothesis": self.hypothesis,
            "baseline_ref": self.baseline_ref,
            "baseline_version": self.baseline_version,
            "candidate_ref": self.candidate_ref,
            "candidate_version": self.candidate_version,
            "scenario_ref": self.scenario_ref,
            "metric_spec": [m.to_dict() for m in self.metric_spec],
            "status": self.status.value,
        }


@dataclass
class PromotionDecision:
    decision: str  # PROMOTION_READY | NOT_PROMOTED | BLOCK
    reason: str = ""
    experiment_id: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "experiment_id": self.experiment_id,
            "metrics": dict(self.metrics),
        }
