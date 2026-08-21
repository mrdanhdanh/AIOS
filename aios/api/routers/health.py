"""Health router — /api/v1/health (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Request
from ..schemas import HealthResponse, ProbeSchema

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, summary="Health check")
async def get_health(request: Request):
    hc = request.app.state.healthcheck
    result = hc.run()
    return HealthResponse(status=result.status.value, probes=[ProbeSchema(name=p.name, healthy=p.healthy, message=p.message) for p in result.probes])


@router.get("/ready", response_model=dict)
async def get_ready(request: Request):
    hc = request.app.state.healthcheck
    return {"ready": hc.is_ready, "status": hc.run().status.value}


@router.get("/live", response_model=dict)
async def get_live():
    return {"live": True}
