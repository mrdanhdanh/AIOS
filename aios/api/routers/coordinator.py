"""Coordinator router — /api/v1/coordinator (TASK-221).

Layering: ``api`` layer. Calls downward into ``aios.agents`` (CoordinatorAgent,
TASK-220). It never executes governance logic itself; it only adapts the HTTP
boundary to the pure agent contract (ARCH-004, downward-only).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException

from aios.agents import CoordinatorAgent, Critic, Reviewer, SpecWriter
from aios.agents.spec_writer import SpecInput

from ..deps import get_kernel  # noqa: F401  (kept for symmetry / future auth)
from ..errors import ApiError, ErrorCode
from ..schemas import (
    CoordinatorRunRequest,
    CoordinatorRunResponse,
    CoordinatorStep,
)

router = APIRouter(prefix="/coordinator", tags=["coordinator"])


@dataclass
class _FakeOrchestrator:
    """Minimal orchestrator for the prototype endpoint.

    The CoordinatorAgent already performs the fail-closed review gate; this
    fake simply records the close intent so the HTTP response reflects the
    coordination outcome. Real deployments should inject a persistent
    Orchestrator bound to the runtime kernel + governance store.
    """

    def advance(self, task_id, to_state, artifacts=None):
        return to_state

    def can_close(self, task_id):
        return True

    def close_if_gate_passes(self, task_id):
        return True


_STORE: Dict[str, CoordinatorRunResponse] = {}


def _build_coordinator(task_id: str) -> CoordinatorAgent:
    return CoordinatorAgent(
        spec_writer=SpecWriter(),
        critic=Critic(),
        reviewer=Reviewer(),
        orchestrator=_FakeOrchestrator(),
    )


@router.post("/run", response_model=CoordinatorRunResponse)
async def run_coordination(body: CoordinatorRunRequest):
    try:
        spec = SpecInput(
            task_id=body.task_id,
            objective=body.objective,
            scope=body.scope,
            deliverables=body.deliverables,
            acceptance=body.acceptance,
            dependencies=body.dependencies,
        )
        coord = _build_coordinator(body.task_id)
        result = coord.coordinate(body.task_id, spec)
        resp = CoordinatorRunResponse(
            task_id=result.task_id,
            approved=result.approved,
            closed=result.closed,
            artifacts=sorted(result.artifacts.keys()),
            steps=[CoordinatorStep(name=s.name, status=s.status, detail=s.detail) for s in result.steps],
        )
        _STORE[body.task_id] = resp
        return resp
    except Exception as exc:  # noqa: BLE001 - surface as contract error
        raise ApiError(ErrorCode.INTERNAL_ERROR, f"Coordination failed: {exc}") from exc


@router.get("/{task_id}", response_model=CoordinatorRunResponse)
async def get_coordination(task_id: str):
    if task_id not in _STORE:
        raise HTTPException(status_code=404, detail=f"No coordination result for {task_id!r}")
    return _STORE[task_id]
