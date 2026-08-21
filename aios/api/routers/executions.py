"""Executions router — /api/v1/executions (TASK-017)."""
from __future__ import annotations
import uuid
from typing import List
from fastapi import APIRouter, Depends, Request
from aios.runtime.policy import PolicyRequest, PolicyDecision
from aios.runtime.state import ExecutionState, RunStatus
from ..deps import get_kernel
from ..errors import ApiError, ErrorCode
from ..schemas import ExecutionCreateRequest, ExecutionResponse, PaginatedResponse, PaginationParams
from ..deps import get_pagination

router = APIRouter(prefix="/executions", tags=["executions"])


def _to_response(eid: str, state) -> ExecutionResponse:
    return ExecutionResponse(execution_id=eid, status=state.status.value if hasattr(state.status, "value") else str(state.status),
        workflow=state.metadata.get("workflow") if isinstance(state.metadata, dict) else None,
        created_at=getattr(state, "created_at", ""), updated_at=getattr(state, "updated_at", ""),
        metadata=dict(state.metadata) if isinstance(state.metadata, dict) else {},
        step_status=dict(state.step_status) if hasattr(state, "step_status") else {})


@router.get("", response_model=PaginatedResponse[ExecutionResponse])
async def list_executions(request: Request, kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination)):
    store = kernel.state
    all_ids: List[str] = store.list_ids() if hasattr(store, "list_ids") else []
    total = len(all_ids)
    page_ids = all_ids[pagination.offset:pagination.offset + pagination.limit]
    items = []
    for eid in page_ids:
        try:
            items.append(_to_response(eid, store.load(eid)))
        except Exception:
            items.append(ExecutionResponse(execution_id=eid, status="UNKNOWN"))
    return PaginatedResponse[ExecutionResponse](items=items, total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=ExecutionResponse, status_code=201)
async def create_execution(body: ExecutionCreateRequest, request: Request, kernel=Depends(get_kernel)):
    auth = getattr(request.state, "auth", None)
    subject = getattr(auth, "subject", "anonymous") if auth else "anonymous"
    result = kernel.policy.evaluate(PolicyRequest(subject=subject, action="execute", resource="execution"))
    if result.decision == PolicyDecision.DENY:
        raise ApiError(ErrorCode.POLICY_DENIED, result.reason or "Policy denied execution")
    eid = kernel.state.new_execution_id() if hasattr(kernel.state, "new_execution_id") else f"exec-{uuid.uuid4().hex[:12]}"
    state = ExecutionState(execution_id=eid, status=RunStatus.CREATED, metadata={"workflow": body.workflow, **body.metadata})
    try: state.transition(RunStatus.PENDING)
    except Exception: pass
    kernel.state.save(state)
    try: request.app.state.event_service.publish("execution.created", {"execution_id": eid, "workflow": body.workflow})
    except Exception: pass
    return _to_response(eid, state)


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str, kernel=Depends(get_kernel)):
    state = kernel.state.load(execution_id)
    if state is None: raise ApiError(ErrorCode.NOT_FOUND, f"Execution {execution_id!r} not found")
    return _to_response(execution_id, state)


@router.delete("/{execution_id}", response_model=dict)
async def cancel_execution(execution_id: str, request: Request, kernel=Depends(get_kernel)):
    state = kernel.state.load(execution_id)
    if state is None: raise ApiError(ErrorCode.NOT_FOUND, f"Execution {execution_id!r} not found")
    try:
        state.transition(RunStatus.CANCELLED)
        kernel.state.save(state)
    except Exception as exc:
        raise ApiError(ErrorCode.CONFLICT, f"Cannot cancel: {exc}") from exc
    try: request.app.state.event_service.publish("execution.failed", {"execution_id": execution_id, "reason": "cancelled"})
    except Exception: pass
    return {"execution_id": execution_id, "status": "cancelled"}


@router.get("/{execution_id}/state", response_model=dict)
async def get_execution_state(execution_id: str, kernel=Depends(get_kernel)):
    state = kernel.state.load(execution_id)
    if state is None: raise ApiError(ErrorCode.NOT_FOUND, f"Execution {execution_id!r} not found")
    return state.to_dict() if hasattr(state, "to_dict") else {"execution_id": execution_id, "status": str(state.status)}
