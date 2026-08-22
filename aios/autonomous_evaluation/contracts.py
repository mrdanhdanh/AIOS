"""Autonomous Evaluation contracts (TASK-060)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(str, Enum):
    CONTINUE = "continue"
    REVISE = "revise"
    RECOVER = "recover"
    ESCALATE = "escalate"
    SAFE_STOP = "safe_stop"
    BLOCK = "block"


@dataclass
class DecisionPolicy:
    """Policy-driven mapping of EvalVerdict → candidate decision.

    Not a hard 1:1 mapping: WARNING/INCONCLUSIVE are resolved by condition
    evaluation rather than a fixed rule.
    """
    # Hard mappings (deterministic, fail-closed).
    pass_decision: Decision = Decision.CONTINUE
    fail_decision: Decision = Decision.RECOVER
    # WARNING resolution depends on `warning_conditions` evaluated at runtime.
    # INCONCLUSIVE resolution depends on `inconclusive_conditions`.
    warning_conditions: dict[str, Decision] = field(default_factory=dict)
    inconclusive_conditions: dict[str, Decision] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pass_decision": self.pass_decision.value,
            "fail_decision": self.fail_decision.value,
            "warning_conditions": {k: v.value for k, v in self.warning_conditions.items()},
            "inconclusive_conditions": {k: v.value for k, v in self.inconclusive_conditions.items()},
        }


@dataclass
class EvaluationRecord:
    record_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    step_id: str = ""
    verdict: str = ""  # PASS/FAIL/WARNING/INCONCLUSIVE/UNKNOWN
    decision_candidate: Decision | None = None
    governor_verdict: str = ""  # ALLOW/BLOCK/ESCALATE
    evidence_ref: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    evaluator_version: str = "1.0"
    policy_version: str = "1.0"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "step_id": self.step_id,
            "verdict": self.verdict,
            "decision_candidate": self.decision_candidate.value if self.decision_candidate else None,
            "governor_verdict": self.governor_verdict,
            "evidence_ref": self.evidence_ref,
            "evaluator_version": self.evaluator_version,
            "policy_version": self.policy_version,
        }
