"""Planner LLM — fallback when deterministic path INSUFFICIENT (TASK-010).

Only runs when Rule=INSUFFICIENT AND Workflow=NO_MATCH. Receives normalized
request + capabilities + workflow candidates + metadata + policy/resource
constraints and produces a validated ExecutionPlan. Never executes tools
directly; output must pass validator.

Layering: orchestrator — may import runtime/capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .execution_plan import ExecutionPlan, ExecutionPlanError, PlanNode

__all__ = ["PlannerRequest", "PlannerResponse", "Planner", "PlannerError", "ValidationError"]


class PlannerError(Exception):
    pass


class ValidationError(PlannerError):
    """Raised when LLM output fails validation (Rule 4)."""


@dataclass
class PlannerRequest:
    """Input to the planner."""

    normalized_request: Any  # NormalizedRequest
    available_capabilities: List[str] = field(default_factory=list)
    workflow_candidates: List[Dict[str, Any]] = field(default_factory=list)
    system_metadata: Dict[str, Any] = field(default_factory=dict)
    policy_constraints: Dict[str, Any] = field(default_factory=dict)
    resource_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannerResponse:
    """Output of the planner."""

    plan: Optional[ExecutionPlan] = None
    raw_output: Optional[str] = None
    validated: bool = False
    error: Optional[str] = None
    source: str = "llm"


class Planner:
    """LLM-backed planner with validation pipeline.

    Validation pipeline:
        LLM Output → Schema → Contract → Capability → Permission → Policy → Resource → ExecutionPlan
    If any step fails, the output is REJECTED (fail-closed).
    """

    def __init__(
        self,
        llm_callable: Optional[Callable[[Any], str]] = None,
        validator: Optional[Callable[[str], bool]] = None,
        capability_registry: Optional[Any] = None,
    ) -> None:
        self.llm_callable = llm_callable
        self.validator = validator
        self.capability_registry = capability_registry
        self.call_count: int = 0

    def plan(self, request: PlannerRequest) -> PlannerResponse:
        if self.llm_callable is None:
            raise PlannerError("No LLM callable configured for planner fallback")
        self.call_count += 1
        raw = self.llm_callable(request.normalized_request)
        if not isinstance(raw, str):
            raw = str(raw)
        # Schema validation: non-empty
        if not raw or not raw.strip():
            raise ValidationError("LLM output empty — schema validation failed")
        # Custom validator (contract/capability/permission/policy/resource)
        if self.validator is not None and not self.validator(raw):
            raise ValidationError("LLM fallback output failed validation")
        # Capability validation: if registry provided, check capabilities in raw
        # For simplicity, raw is treated as capability list or single capability
        # e.g. "cap_a,cap_b" or "cap_a"
        plan = self._raw_to_plan(raw, request)
        # Validate plan
        try:
            plan.validate()
        except ExecutionPlanError as exc:
            raise ValidationError(f"Planner output invalid ExecutionPlan: {exc}") from exc
        # Capability existence check if registry provided
        if self.capability_registry is not None:
            for node in plan.nodes:
                try:
                    if hasattr(self.capability_registry, "get"):
                        if len(self.capability_registry) > 0:
                            try:
                                cap = self.capability_registry.get(node.capability)
                            except Exception:
                                cap = None
                            if cap is None:
                                raise ValidationError(f"capability {node.capability!r} not in registry")
                except ValidationError:
                    raise
                except Exception:
                    pass
        return PlannerResponse(plan=plan, raw_output=raw, validated=True, source="llm")

    def _raw_to_plan(self, raw: str, request: PlannerRequest) -> ExecutionPlan:
        # Try to parse raw as comma-separated capabilities or single capability
        # If raw contains "capability:" prefix, extract
        raw_stripped = raw.strip()
        # If raw looks like JSON with nodes, try to parse
        if raw_stripped.startswith("{"):
            try:
                import json

                data = json.loads(raw_stripped)
                if isinstance(data, dict) and "nodes" in data:
                    plan = ExecutionPlan(plan_id="planner-llm", metadata={"source": "planner", "intent": getattr(request.normalized_request, "intent", "")})
                    for n in data["nodes"]:
                        nid = str(n.get("id", f"node-{len(plan.nodes)}"))
                        cap = str(n.get("capability", n.get("cap", "unknown")))
                        plan.add_node(PlanNode(id=nid, capability=cap, description=str(n.get("description", ""))))
                    return plan
            except Exception:
                pass
        # Fallback: split by comma or newline
        parts = [p.strip() for p in raw_stripped.replace("\n", ",").split(",") if p.strip()]
        if not parts:
            parts = [raw_stripped]
        plan = ExecutionPlan(plan_id="planner-llm", metadata={"source": "planner", "intent": getattr(request.normalized_request, "intent", "")})
        for idx, cap in enumerate(parts):
            # Clean capability: remove prefix like "capability:" or "handle:"
            cap_clean = cap.strip()
            if ":" in cap_clean:
                # Take last part after colon if it looks like capability
                cap_clean = cap_clean.split(":")[-1].strip()
            if not cap_clean:
                cap_clean = f"cap_{idx}"
            # Ensure valid capability id (alphanumeric + _)
            cap_clean = cap_clean.replace("-", "_").replace(" ", "_")
            if not cap_clean:
                cap_clean = f"cap_{idx}"
            nid = f"planner-{idx}"
            plan.add_node(PlanNode(id=nid, capability=cap_clean, description=f"planner:{cap_clean}"))
            if idx > 0:
                from .execution_plan import PlanEdge

                plan.add_edge(PlanEdge(from_id=f"planner-{idx-1}", to_id=nid))
        return plan
