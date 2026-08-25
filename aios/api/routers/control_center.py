"""Control Center router — /api/v1/control-center (TASK-237, M34).

Read-only unified snapshot of all AIOS planes. The frontend only renders;
this router performs no business logic, it delegates to the dashboard
aggregator (presentation boundary, layering: api -> dashboard).
"""
from __future__ import annotations

from fastapi import APIRouter, Request

from aios.dashboard.control_center import ControlCenterAggregator

router = APIRouter(prefix="/control-center", tags=["control-center"])


@router.get("", response_model=dict)
async def get_control_center(request: Request) -> dict:
    """Return a unified, fail-isolated snapshot of every plane."""
    kernel = request.app.state.kernel
    health = request.app.state.healthcheck
    try:
        system_health = health.run().status.value
    except Exception:  # fail-closed: degrade gracefully
        system_health = "unknown"

    # Lightweight, fail-isolated collectors from kernel/runtime state.
    def _kernel_stats() -> dict:
        return kernel.health()

    agg = ControlCenterAggregator(collectors={"system_health": lambda: {"status": system_health}})
    agg.register("resources", _kernel_stats)
    snapshot = agg.snapshot(system_health=system_health)
    return snapshot.to_dict()
