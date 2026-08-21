"""Workflows router — /api/v1/workflows (TASK-017)."""
from __future__ import annotations
import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends
from aios.runtime.workflow.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from aios.runtime.workflow.validation import validate_definition
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import PaginatedResponse, PaginationParams, WorkflowCreateRequest, WorkflowResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])
_store: Dict[str, Dict[str, Any]] = {}


@router.get("", response_model=PaginatedResponse[WorkflowResponse])
async def list_workflows(pagination: PaginationParams = Depends(get_pagination)):
    all_items = sorted(_store.values(), key=lambda w: w["workflow_id"])
    total = len(all_items)
    page = all_items[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[WorkflowResponse](items=[WorkflowResponse(**w) for w in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(body: WorkflowCreateRequest):
    nodes = [WorkflowNode.from_dict(n) for n in body.nodes]
    edges = [WorkflowEdge.from_dict(e) for e in body.edges]
    definition = WorkflowDefinition(name=body.name, version=body.version, description=body.description, nodes=nodes, edges=edges, retries=body.retries, timeout=body.timeout)
    validate_definition(definition)
    wid = f"wf-{uuid.uuid4().hex[:12]}"
    data = {"workflow_id": wid, "name": body.name, "version": body.version, "description": body.description,
            "nodes": body.nodes, "edges": body.edges, "metadata": {"retries": body.retries, "timeout": body.timeout}}
    _store[wid] = data
    return WorkflowResponse(**data)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    wf = _store.get(workflow_id)
    if wf is None: raise ApiError(ErrorCode.NOT_FOUND, f"Workflow {workflow_id!r} not found")
    return WorkflowResponse(**wf)


@router.delete("/{workflow_id}", response_model=dict)
async def delete_workflow(workflow_id: str):
    if workflow_id not in _store: raise ApiError(ErrorCode.NOT_FOUND, f"Workflow {workflow_id!r} not found")
    del _store[workflow_id]
    return {"deleted": workflow_id}
