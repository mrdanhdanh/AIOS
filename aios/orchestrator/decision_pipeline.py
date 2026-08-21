"""Decision Pipeline — orchestration of Normalizer → Rule → Workflow → Planner → Policy (TASK-010).

Deterministic-first: LLM only when Rule=INSUFFICIENT AND Workflow=NO_MATCH.
Evidence chain: Request → NormalizedRequest → Decision → Workflow/Planner → ExecutionPlan.
Offline-first: deterministic requests run without LLM.
Fail-closed: invalid planner output or policy DENY → REJECT.

Layering: orchestrator — may import runtime/capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from .execution_plan import ExecutionPlan, ExecutionPlanError
from .normalizer import Normalizer, NormalizedRequest
from .planner import Planner, PlannerError, PlannerRequest, ValidationError
from .rule_engine import RuleDecision, RuleEngine
from .workflow_matcher import WorkflowLibrary, WorkflowMatcher

__all__ = ["DecisionEvidence", "DecisionResult", "DecisionPipeline", "DecisionPipelineError"]


class DecisionPipelineError(Exception):
    pass


@dataclass
class DecisionEvidence:
    """Provenance chain for a decision."""

    request_text: str
    normalized: NormalizedRequest
    rule_decision: RuleDecision
    workflow_matched: bool
    workflow_id: Optional[str] = None
    planner_called: bool = False
    planner_raw: Optional[str] = None
    plan: Optional[ExecutionPlan] = None
    policy_checked: bool = False
    policy_allowed: Optional[bool] = None
    llm_call_count: int = 0
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "deterministic"  # deterministic | workflow | llm

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_text": self.request_text,
            "normalized": self.normalized.to_dict(),
            "rule_decision": {"status": self.rule_decision.status, "reason": self.rule_decision.reason, "matched_rule": self.rule_decision.matched_rule},
            "workflow_matched": self.workflow_matched,
            "workflow_id": self.workflow_id,
            "planner_called": self.planner_called,
            "planner_raw": self.planner_raw,
            "plan": self.plan.to_dict() if self.plan else None,
            "policy_checked": self.policy_checked,
            "policy_allowed": self.policy_allowed,
            "llm_call_count": self.llm_call_count,
            "source": self.source,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class DecisionResult:
    """Result of DecisionPipeline.execute."""

    plan: ExecutionPlan
    evidence: DecisionEvidence
    source: str = "deterministic"
    llm_call_count: int = 0


class DecisionPipeline:
    """Ordered deterministic control path (TASK-010).

    Pipeline:
        Request → Normalizer → RuleEngine → WorkflowMatcher → Planner → Policy → ExecutionPlan
    """

    def __init__(
        self,
        normalizer: Optional[Normalizer] = None,
        rule_engine: Optional[RuleEngine] = None,
        workflow_matcher: Optional[WorkflowMatcher] = None,
        planner: Optional[Planner] = None,
        policy_checker: Optional[Callable[[ExecutionPlan], bool]] = None,
        capability_resolver: Optional[Callable[[ExecutionPlan], ExecutionPlan]] = None,
    ) -> None:
        self.normalizer = normalizer or Normalizer()
        self.rule_engine = rule_engine or RuleEngine()
        self.workflow_matcher = workflow_matcher or WorkflowMatcher()
        self.planner = planner
        self.policy_checker = policy_checker
        self.capability_resolver = capability_resolver
        self.llm_call_count: int = 0

    def execute(self, request: Any) -> DecisionResult:
        started = datetime.now(timezone.utc).isoformat()
        # Extract raw text for evidence
        if isinstance(request, dict):
            raw_text = str(request.get("text", "") or "")
        else:
            raw_text = str(getattr(request, "text", "") or "")

        # Stage 1: Normalizer
        nr: NormalizedRequest = self.normalizer.normalize(request)

        # Stage 2: Rule Engine
        decision: RuleDecision = self.rule_engine.decide(nr)

        workflow_matched = False
        workflow_id: Optional[str] = None
        planner_called = False
        planner_raw: Optional[str] = None
        source = "deterministic"

        plan: Optional[ExecutionPlan] = None

        if decision.status == "SUFFICIENT":
            plan = decision.plan
            source = "deterministic"
        else:
            # Stage 3: Workflow Matcher
            before_status = decision.status
            decision = self.workflow_matcher.match(decision)  # type: ignore
            # Check if workflow made it SUFFICIENT
            if getattr(decision, "status", "INSUFFICIENT") == "SUFFICIENT":
                plan = getattr(decision, "plan", None)
                workflow_matched = True
                workflow_id = getattr(decision, "matched_rule", None)
                if workflow_id and workflow_id.startswith("workflow:"):
                    workflow_id = workflow_id.split(":", 1)[1]
                source = "workflow"
            else:
                # Stage 4: Planner LLM (only here)
                if self.planner is None:
                    raise DecisionPipelineError("Deterministic path insufficient and no planner configured")
                # Build PlannerRequest
                caps: List[str] = []
                if self.workflow_matcher and hasattr(self.workflow_matcher, "library"):
                    try:
                        caps = [str(c) for wf in self.workflow_matcher.library.list() for c in wf.get("capabilities", [])]  # type: ignore
                    except Exception:
                        caps = []
                preq = PlannerRequest(
                    normalized_request=nr,
                    available_capabilities=caps,
                    workflow_candidates=self.workflow_matcher.library.list() if hasattr(self.workflow_matcher, "library") else [],
                    system_metadata=dict(getattr(nr, "metadata", {}) or {}),
                    policy_constraints={},
                    resource_constraints={},
                )
                try:
                    presp = self.planner.plan(preq)
                except ValidationError:
                    raise
                except PlannerError:
                    raise
                except Exception as exc:
                    raise DecisionPipelineError(f"Planner failed: {exc}") from exc
                self.llm_call_count += 1
                # Also increment planner's count already done inside planner
                planner_called = True
                planner_raw = presp.raw_output
                plan = presp.plan
                source = "llm"

        if plan is None:
            raise DecisionPipelineError("No execution plan produced by pipeline")

        # Capability resolver (optional)
        if self.capability_resolver is not None:
            plan = self.capability_resolver(plan)

        # Validate plan
        try:
            plan.validate()
        except ExecutionPlanError as exc:
            raise ValidationError(f"ExecutionPlan validation failed: {exc}") from exc

        # Policy pre-check
        policy_checked = False
        policy_allowed: Optional[bool] = None
        if self.policy_checker is not None:
            policy_checked = True
            allowed = self.policy_checker(plan)
            policy_allowed = bool(allowed)
            if not allowed:
                raise DecisionPipelineError("ExecutionPlan rejected by policy")

        completed = datetime.now(timezone.utc).isoformat()
        evidence = DecisionEvidence(
            request_text=raw_text,
            normalized=nr,
            rule_decision=decision,
            workflow_matched=workflow_matched,
            workflow_id=workflow_id,
            planner_called=planner_called,
            planner_raw=planner_raw,
            plan=plan,
            policy_checked=policy_checked,
            policy_allowed=policy_allowed,
            llm_call_count=self.llm_call_count,
            started_at=started,
            completed_at=completed,
            source=source,
        )
        return DecisionResult(plan=plan, evidence=evidence, source=source, llm_call_count=self.llm_call_count)
