"""Deterministic control path implementation (Rule 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


class ValidationError(Exception):
    """Raised when LLM fallback output fails validation."""


@dataclass
class Request:
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class NormalizedRequest:
    intent: str
    signals: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    steps: List[str]
    source: str = "deterministic"  # or "llm"
    raw: Optional[str] = None


@dataclass
class RuleDecision:
    # status is either "SUFFICIENT" or "INSUFFICIENT".
    status: str
    plan: Optional[ExecutionPlan] = None
    reason: str = ""


# --------------------------------------------------------------------------- #
# Pipeline stages (each is a small, injectable component)
# --------------------------------------------------------------------------- #
class Normalizer:
    """Stage 1: normalize a raw request into a typed intent."""

    def normalize(self, request: Request) -> NormalizedRequest:
        intent = (request.text or "").strip().lower()
        return NormalizedRequest(intent=intent, signals=dict(request.metadata))


class RuleEngine:
    """Stage 2: deterministic rules over the normalized request.

    Subclasses override :meth:`decide`. The default implementation decides
    SUFFICIENT only for a known, hard-coded intent.
    """

    KNOWN_INTENTS = {"status", "health", "help", "list tasks"}

    def decide(self, nr: NormalizedRequest) -> RuleDecision:
        if nr.intent in self.KNOWN_INTENTS:
            return RuleDecision(
                status="SUFFICIENT",
                plan=ExecutionPlan(steps=[f"handle:{nr.intent}"]),
                reason="matched deterministic rule",
            )
        return RuleDecision(
            status="INSUFFICIENT",
            reason="no deterministic rule matched the intent",
        )


class WorkflowMatcher:
    """Stage 3: map a rule decision to a workflow (kept separate for clarity)."""

    def match(self, decision: RuleDecision) -> RuleDecision:
        return decision


class CapabilityResolver:
    """Stage 5: resolve an execution plan to concrete capabilities."""

    def resolve(self, plan: Optional[ExecutionPlan]) -> Optional[ExecutionPlan]:
        return plan


class Policy:
    """Stage 6: policy pre-check on the resolved plan."""

    def check(self, plan: Optional[ExecutionPlan]) -> bool:
        return plan is not None and len(plan.steps) > 0


# --------------------------------------------------------------------------- #
# Control path
# --------------------------------------------------------------------------- #
class DeterministicControlPath:
    """The ordered deterministic control path (Rule 4)."""

    def __init__(
        self,
        normalizer: Optional[Normalizer] = None,
        rule_engine: Optional[RuleEngine] = None,
        workflow_matcher: Optional[WorkflowMatcher] = None,
        capability_resolver: Optional[CapabilityResolver] = None,
        policy: Optional[Policy] = None,
        llm_fallback: Optional[Callable[[NormalizedRequest], str]] = None,
        validator: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self.normalizer = normalizer or Normalizer()
        self.rule_engine = rule_engine or RuleEngine()
        self.workflow_matcher = workflow_matcher or WorkflowMatcher()
        self.capability_resolver = capability_resolver or CapabilityResolver()
        self.policy = policy or Policy()
        self.llm_fallback = llm_fallback
        self.validator = validator
        self.llm_call_count: int = 0

    def execute(self, request: Request) -> ExecutionPlan:
        # Request -> Normalizer
        nr = self.normalizer.normalize(request)
        # Normalizer -> Rule Engine
        decision = self.rule_engine.decide(nr)
        # Rule Engine -> Workflow Matcher
        decision = self.workflow_matcher.match(decision)

        if decision.status == "SUFFICIENT":
            # Capability Resolver -> Policy -> Execution Plan (no LLM).
            plan = self.capability_resolver.resolve(decision.plan)
            if not self.policy.check(plan):
                raise RuntimeError("Deterministic plan rejected by policy.")
            plan.source = "deterministic"
            return plan

        # Deterministic INSUFFICIENT -> LLM fallback (only here).
        if self.llm_fallback is None:
            raise RuntimeError("Deterministic path insufficient and no LLM fallback configured.")
        self.llm_call_count += 1
        raw = self.llm_fallback(nr)
        if self.validator is not None and not self.validator(raw):
            raise ValidationError("LLM fallback output failed validation.")
        plan = ExecutionPlan(steps=[raw], source="llm", raw=raw)
        plan = self.capability_resolver.resolve(plan)
        if not self.policy.check(plan):
            raise RuntimeError("LLM-derived plan rejected by policy.")
        return plan
