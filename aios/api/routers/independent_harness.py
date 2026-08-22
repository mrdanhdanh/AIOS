"""Independent Harness console router — /api/v1/independent-harness (TASK-108).

Presentation boundary for the Management Console / Independent Harness
Integration. The console only *displays*; operator actions are policy-gated
and dispatched through the API/runtime (AIOS retains authority).

Layering: ``api`` layer. Imports the ``unknown``-layer ``aios.independent_harness``.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from aios.independent_harness import (
    HarnessRegistry,
    HarnessType,
    IndependentHarnessAdapter,
    ManagementConsoleIntegration,
)

router = APIRouter(prefix="/independent-harness", tags=["independent-harness"])

# Module-level singletons back the console (demo wiring; production would inject
# these via the kernel/container). Kept in-memory and deterministic.
_REGISTRY = HarnessRegistry()
_CONSOLE = ManagementConsoleIntegration()


class RegisterRequest(BaseModel):
    harness_id: str
    harness_type: str = "external"
    source: str = ""
    supported_checks: list[str] = Field(default_factory=list)


class ActionRequest(BaseModel):
    console_id: str
    action: str
    policy_gate_allowed: bool = False


class StatusResponse(BaseModel):
    console_id: str
    harness_status: str
    independent_results_summary: dict
    aios_authority_flag: str
    operator_action: str
    evidence_ref: str


@router.post("/register", summary="Register an independent harness")
async def register(req: RegisterRequest):
    try:
        htype = HarnessType(req.harness_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid harness_type")
    adapter = IndependentHarnessAdapter(
        harness_id=req.harness_id,
        harness_type=htype,
        source=req.source,
        supported_checks=req.supported_checks,
    )
    try:
        _REGISTRY.register(adapter)
    except Exception as exc:  # T001 Rule 1 — duplicate id rejected
        raise HTTPException(status_code=409, detail=str(exc))
    return {"registered": True, "harness_id": req.harness_id}


@router.get("/status", response_model=StatusResponse, summary="Console harness status")
async def status(console_id: str = "console-default", harness_id: str = ""):
    view = _CONSOLE.aggregate(
        console_id=console_id,
        harness_id=harness_id or "unregistered",
    )
    return StatusResponse(**view.to_dict())


@router.post("/action", summary="Policy-gated operator action")
async def action(req: ActionRequest):
    result = _CONSOLE.request_operator_action(req.action, req.policy_gate_allowed)
    if not result.get("dispatched"):
        raise HTTPException(status_code=403, detail=result.get("reason", "denied"))
    return result
