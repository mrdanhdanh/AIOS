"""System router — /api/v1/system (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from ..deps import get_kernel
from ..schemas import HealthResponse, ProbeSchema, SystemInfoResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("", response_model=SystemInfoResponse)
async def get_system(request: Request, kernel=Depends(get_kernel)):
    hc = request.app.state.healthcheck
    result = hc.run()
    return SystemInfoResponse(health=HealthResponse(status=result.status.value, probes=[ProbeSchema(name=p.name, healthy=p.healthy, message=p.message) for p in result.probes]), kernel_stats=kernel.health())


@router.get("/info", response_model=dict)
async def get_info(kernel=Depends(get_kernel)):
    return {"kernel_stats": kernel.health(), "version": "0.2.0"}


@router.get("/config", response_model=dict)
async def get_config(request: Request):
    return request.app.state.config.as_dict()
