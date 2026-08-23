"""Coding Planner + PlanVerifier (TASK-126, M19).

Deterministic-first coding planner: rules decide the plan when they are
sufficient (LLM call count = 0, T001 Rule 4). PlanVerifier validates a plan
(schema, dependency, policy) before execution and fails closed (T078). Every
plan carries provenance (T001 Rule 5) and is deterministic: same request + same
rules -> same plan.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class PlanVerifyError(Exception):
    """Raised when a plan fails verification (fail-closed, T078)."""


@dataclass(frozen=True)
class CodingStep:
    action: str
    target: str
    policy_ref: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "target": self.target,
            "policy_ref": self.policy_ref,
        }


@dataclass
class CodingPlan:
    plan_id: str
    agent_ref: str
    steps: List[CodingStep]
    planner_deterministic: bool
    verified: bool
    llm_call_count: int
    evidence_id: str
    content_hash: str
    status: PlanStatus = PlanStatus.DRAFT

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "agent_ref": self.agent_ref,
            "steps": [s.to_dict() for s in self.steps],
            "planner_deterministic": self.planner_deterministic,
            "verified": self.verified,
            "llm_call_count": self.llm_call_count,
            "evidence_id": self.evidence_id,
            "content_hash": self.content_hash,
            "status": self.status.value,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# Deterministic rule table: intent keyword -> ordered coding steps.
# When a request matches a known intent, the planner is fully deterministic
# (LLM call count = 0, T001 Rule 4).
_KNOWN_INTENTS: Dict[str, List[Tuple[str, str]]] = {
    "add function": [
        ("create", "src/<module>.py::<fn>"),
        ("test", "tests/test_<module>.py"),
        ("lint", "src/<module>.py"),
    ],
    "fix bug": [
        ("locate", "src/<module>.py"),
        ("patch", "src/<module>.py::<fn>"),
        ("test", "tests/test_<module>.py"),
    ],
    "refactor": [
        ("analyze", "src/<module>.py"),
        ("refactor", "src/<module>.py"),
        ("test", "tests/test_<module>.py"),
    ],
}


class CodingPlanner:
    """Deterministic-first coding planner (T126)."""

    def __init__(self, agent_ref: str = "coder-1") -> None:
        self._agent_ref = agent_ref

    def plan(self, request: str, llm_fallback=None) -> CodingPlan:
        """Build a coding plan.

        Deterministic path: a known intent -> rule-based steps, llm_call_count=0.
        Insufficient path: only when no rule matches, call ``llm_fallback``
        (optional) and count the call; output must be validated by PlanVerifier.
        """
        intent, steps = self._match_rule(request)
        llm_calls = 0
        if steps is None:
            if llm_fallback is None:
                # Deterministic-only: refuse to guess (fail-closed on unknown).
                steps = []
            else:
                llm_calls = 1
                steps = llm_fallback(request) or []
        deterministic = llm_calls == 0
        coding_steps = [CodingStep(action=a, target=t) for a, t in steps]
        content = f"{self._agent_ref}:{intent}:{[(s.action, s.target) for s in coding_steps]}"
        plan = CodingPlan(
            plan_id=f"plan-{uuid.uuid4().hex[:12]}",
            agent_ref=self._agent_ref,
            steps=coding_steps,
            planner_deterministic=deterministic,
            verified=False,
            llm_call_count=llm_calls,
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
            content_hash=_hash(content),
        )
        return plan

    def _match_rule(self, request: str) -> Tuple[str, Optional[List[Tuple[str, str]]]]:
        lowered = (request or "").lower()
        for intent, steps in _KNOWN_INTENTS.items():
            if intent in lowered:
                return intent, steps
        return "unknown", None


class PlanVerifier:
    """Verify a coding plan before execution (fail-closed, T078)."""

    # A well-formed plan must mutate code and verify it: at least one mutating
    # action (create/patch/refactor) and at least one test action.
    _MUTATING_ACTIONS: Set[str] = {"create", "patch", "refactor"}

    def verify(self, plan: CodingPlan, policy_ok: bool = True) -> CodingPlan:
        """Validate ``plan``; raise PlanVerifyError on failure (fail-closed)."""
        errors: List[str] = []
        if not plan.steps:
            errors.append("plan has no steps")
        actions = {s.action for s in plan.steps}
        if not (actions & self._MUTATING_ACTIONS):
            errors.append("plan has no mutating action (create/patch/refactor)")
        if "test" not in actions:
            errors.append("plan has no test action")
        for s in plan.steps:
            if not re.match(r"^[a-zA-Z0-9_.<>:/-]+$", s.target):
                errors.append(f"invalid target: {s.target}")
        if not policy_ok:
            errors.append("policy rejected plan (T113)")
        if errors:
            plan.status = PlanStatus.REJECTED
            raise PlanVerifyError("; ".join(errors))
        plan.verified = True
        plan.status = PlanStatus.VERIFIED
        return plan
