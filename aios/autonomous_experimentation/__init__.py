"""Autonomous Experimentation (TASK-058).

A capability that proposes and runs improvement experiments *under the existing
Harness* (T029–T034) with verification + evaluation, reversible and
fail-closed. The Experiment Controller only produces a `PromotionDecision`
artifact — it never self-deploys a production change and never creates a
sandbox/control plane of its own.
"""

from aios.autonomous_experimentation.contracts import (
    Experiment,
    ExperimentStatus,
    PromotionDecision,
)
from aios.autonomous_experimentation.controller import ExperimentController

__all__ = [
    "Experiment",
    "ExperimentStatus",
    "PromotionDecision",
    "ExperimentController",
]
