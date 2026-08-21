"""Agents router — /api/v1/agents (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import AgentResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/agents", tags=["agents"])

_KNOWN = [
    {"agent_id": "general-worker", "agent_type": "GENERAL", "status": "READY", "health": "READY", "capabilities": ["research", "summarize"]},
    {"agent_id": "coder-worker", "agent_type": "CODER", "status": "READY", "health": "READY", "capabilities": ["code.read", "code.write"]},
    {"agent_id": "doctor-worker", "agent_type": "DOCTOR", "status": "READY", "health": "READY", "capabilities": ["diagnose.task"]},
    {"agent_id": "system-doctor-worker", "agent_type": "SYSTEM_DOCTOR", "status": "READY", "health": "READY", "capabilities": ["diagnose.runtime"]},
]


@router.get("", response_model=PaginatedResponse[AgentResponse])
async def list_agents(pagination: PaginationParams = Depends(get_pagination)):
    total = len(_KNOWN)
    page = _KNOWN[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[AgentResponse](items=[AgentResponse(**a) for a in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    for a in _KNOWN:
        if a["agent_id"] == agent_id:
            return AgentResponse(**a)
    raise ApiError(ErrorCode.NOT_FOUND, f"Agent {agent_id!r} not found")
