"""Orchestrator router — /api/v1/orchestrator (TASK-017)."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, Request
from aios.orchestrator.decision_pipeline import DecisionPipeline
from aios.orchestrator.normalizer import Normalizer
from aios.orchestrator.rule_engine import RuleEngine
from aios.orchestrator.workflow_matcher import WorkflowLibrary, WorkflowMatcher
from ..deps import get_kernel
from ..errors import ApiError, ErrorCode
from ..schemas import OrchestratorDecideRequest, OrchestratorDecideResponse

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])


def _get_pipeline() -> DecisionPipeline:
    return DecisionPipeline(
        normalizer=Normalizer(), rule_engine=RuleEngine(),
        workflow_matcher=WorkflowMatcher(library=WorkflowLibrary()), planner=None)


@router.post("/decide", response_model=OrchestratorDecideResponse)
async def decide(body: OrchestratorDecideRequest, request: Request, kernel=Depends(get_kernel)):
    try:
        result = _get_pipeline().execute({"text": body.text, "context_id": body.context_id, "metadata": body.metadata})
    except Exception as exc:
        if "insufficient" in str(exc).lower() or "no planner" in str(exc).lower():
            raise ApiError(ErrorCode.CONTRACT_INVALID, f"Decision insufficient: {exc}") from exc
        raise ApiError(ErrorCode.INTERNAL_ERROR, f"Decision failed: {exc}") from exc
    plan = result.plan
    nodes, edges = [], []
    if plan is not None:
        if hasattr(plan, "nodes"):
            nodes = [n.to_dict() if hasattr(n, "to_dict") else {"id": getattr(n, "id", str(n))} for n in plan.nodes]
        if hasattr(plan, "edges"):
            edges = [e.to_dict() if hasattr(e, "to_dict") else {"from_id": getattr(e, "from_id", ""), "to_id": getattr(e, "to_id", "")} for e in plan.edges]
    evidence = result.evidence.to_dict() if hasattr(result, "evidence") and hasattr(result.evidence, "to_dict") else {}
    plan_id = getattr(plan, "plan_id", f"plan-{uuid.uuid4().hex[:12]}") if plan else f"plan-{uuid.uuid4().hex[:12]}"
    return OrchestratorDecideResponse(plan_id=str(plan_id), source=getattr(result, "source", "deterministic"),
        llm_call_count=getattr(result, "llm_call_count", 0), nodes=nodes, edges=edges, evidence=evidence)


@router.get("/status", response_model=dict)
async def get_status(kernel=Depends(get_kernel)):
    return {"status": "ready", "kernel_stats": kernel.health()}
