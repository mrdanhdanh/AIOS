"""Tasks router — /api/v1/tasks (TASK-017)."""
from __future__ import annotations
import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, Request
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import PaginatedResponse, PaginationParams, TaskCreateRequest, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])
_store: Dict[str, Dict[str, Any]] = {}


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(pagination: PaginationParams = Depends(get_pagination)):
    all_items = sorted(_store.values(), key=lambda t: t["task_id"])
    total = len(all_items)
    page = all_items[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[TaskResponse](items=[TaskResponse(**t) for t in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(body: TaskCreateRequest, request: Request):
    tid = f"task-{uuid.uuid4().hex[:12]}"
    data = {"task_id": tid, "title": body.title, "description": body.description, "status": "PENDING",
            "priority": body.priority, "goal_id": body.goal_id, "dependencies": body.dependencies, "metadata": body.metadata}
    _store[tid] = data
    try: request.app.state.event_service.publish("task.created", {"task_id": tid, "title": body.title})
    except Exception: pass
    return TaskResponse(**data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    t = _store.get(task_id)
    if t is None: raise ApiError(ErrorCode.NOT_FOUND, f"Task {task_id!r} not found")
    return TaskResponse(**t)
