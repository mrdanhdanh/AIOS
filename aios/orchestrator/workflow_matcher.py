"""Workflow Matcher — map INSUFFICIENT decisions to WorkflowLibrary (TASK-010).

Deterministic, no LLM. If a workflow matches, returns SUFFICIENT with an
ExecutionPlan derived from the workflow definition.

Layering: orchestrator — may import runtime.workflow for validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .execution_plan import ExecutionPlan, PlanEdge, PlanNode

__all__ = ["WorkflowMatch", "WorkflowLibrary", "WorkflowMatcher", "WorkflowMatcherError"]


class WorkflowMatcherError(Exception):
    pass


@dataclass
class WorkflowMatch:
    status: str  # MATCHED | NO_MATCH
    workflow_id: Optional[str] = None
    reason: str = ""


class WorkflowLibrary:
    """In-memory workflow registry for matcher (deterministic)."""

    def __init__(self) -> None:
        self._workflows: Dict[str, Dict[str, object]] = {}

    def register(self, workflow_id: str, *, capabilities: List[str], description: str = "", tags: Optional[List[str]] = None) -> None:
        if not workflow_id or not workflow_id.strip():
            raise WorkflowMatcherError("workflow_id must be non-empty")
        if workflow_id in self._workflows:
            raise WorkflowMatcherError(f"workflow {workflow_id!r} already registered")
        self._workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "capabilities": list(capabilities),
            "description": description,
            "tags": list(tags or []),
        }

    def get(self, workflow_id: str) -> Optional[Dict[str, object]]:
        return self._workflows.get(workflow_id)

    def list(self) -> List[Dict[str, object]]:
        return list(self._workflows.values())

    def find_for_intent(self, intent: str) -> Optional[Dict[str, object]]:
        import re

        def _tokens(s: str) -> set[str]:
            return set(t for t in re.split(r"[^a-z0-9]+", s.lower()) if t)

        intent_l = intent.lower().strip()
        intent_tokens = _tokens(intent_l)
        # Exact workflow_id match
        if intent_l in self._workflows:
            return self._workflows[intent_l]
        # Substring / capability / token overlap match
        for wf in self._workflows.values():
            wid = str(wf["workflow_id"]).lower()
            if intent_l in wid or wid in intent_l:
                return wf
            wid_tokens = _tokens(wid)
            if intent_tokens & wid_tokens:
                return wf
            for cap in wf.get("capabilities", []):  # type: ignore
                cap_l = str(cap).lower()
                if intent_l in cap_l or cap_l in intent_l:
                    return wf
                if intent_tokens & _tokens(cap_l):
                    return wf
            for tag in wf.get("tags", []):  # type: ignore
                tag_l = str(tag).lower()
                if intent_l == tag_l:
                    return wf
                if intent_tokens & _tokens(tag_l):
                    return wf
            # Also check description tokens
            desc = str(wf.get("description", "")).lower()
            if desc and intent_tokens & _tokens(desc):
                return wf
        return None

    def clear(self) -> None:
        self._workflows.clear()

    def __len__(self) -> int:
        return len(self._workflows)


class WorkflowMatcher:
    """Stage 3: map a rule decision to a workflow."""

    def __init__(self, library: Optional[WorkflowLibrary] = None) -> None:
        self.library = library or WorkflowLibrary()

    def match(self, decision) -> object:
        # decision is RuleDecision; if already SUFFICIENT, pass through
        status = getattr(decision, "status", "INSUFFICIENT")
        if status == "SUFFICIENT":
            return decision
        intent = getattr(decision, "intent", "") or ""
        wf = self.library.find_for_intent(intent)
        if wf is not None:
            # Build ExecutionPlan from workflow
            caps = list(wf.get("capabilities", []))  # type: ignore
            plan = ExecutionPlan(plan_id=f"wf-{wf['workflow_id']}", metadata={"source": "workflow_matcher", "workflow_id": wf["workflow_id"], "intent": intent})
            prev_id: Optional[str] = None
            for idx, cap in enumerate(caps):
                nid = f"wf-{wf['workflow_id']}-{idx}"
                plan.add_node(PlanNode(id=nid, capability=str(cap), description=f"workflow:{wf['workflow_id']}:{cap}"))
                if prev_id is not None:
                    plan.add_edge(PlanEdge(from_id=prev_id, to_id=nid))
                prev_id = nid
            # Attach match info to decision
            decision.status = "SUFFICIENT"
            decision.plan = plan
            decision.reason = f"matched workflow {wf['workflow_id']!r}"
            decision.matched_rule = f"workflow:{wf['workflow_id']}"
            return decision
        # No match — remain INSUFFICIENT
        return decision

    # Convenience for tests: direct intent match
    def match_intent(self, intent: str) -> WorkflowMatch:
        wf = self.library.find_for_intent(intent)
        if wf is not None:
            return WorkflowMatch(status="MATCHED", workflow_id=str(wf["workflow_id"]), reason=f"matched {wf['workflow_id']!r}")
        return WorkflowMatch(status="NO_MATCH", reason="no workflow matched")
