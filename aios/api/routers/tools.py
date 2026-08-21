"""Tools router — /api/v1/tools (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from aios.tool.contracts import ToolContract, ToolType
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import PaginatedResponse, PaginationParams, ToolCreateRequest, ToolResponse

router = APIRouter(prefix="/tools", tags=["tools"])


def _to_resp(c) -> ToolResponse:
    return ToolResponse(tool_id=c.tool_id, name=c.name, version=c.version,
        tool_type=c.tool_type.value if hasattr(c.tool_type, "value") else str(c.tool_type),
        description=c.description, capabilities=list(c.capabilities),
        health=c.health.value if hasattr(c.health, "value") else str(c.health),
        priority=c.priority, enabled=c.enabled)


@router.get("", response_model=PaginatedResponse[ToolResponse])
async def list_tools(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination),
                     capability: str = Query(default=None), q: str = Query(default=None)):
    reg = kernel.tools
    contracts = reg.find_by_capability(capability) if capability else reg.find(q) if q else reg.list()
    total = len(contracts)
    page = contracts[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[ToolResponse](items=[_to_resp(c) for c in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=ToolResponse, status_code=201)
async def create_tool(body: ToolCreateRequest, kernel=Depends(get_kernel)):
    try: ttype = ToolType(body.tool_type.lower())
    except ValueError as exc: raise ApiError(ErrorCode.CONTRACT_INVALID, f"Invalid tool_type: {exc}") from exc
    contract = ToolContract.create(tool_id=body.tool_id, name=body.name, version=body.version, tool_type=ttype,
        description=body.description, capabilities=body.capabilities, permissions=body.permissions, resources=body.resources, priority=body.priority)
    try: kernel.tools.register(contract)
    except Exception as exc: raise ApiError(ErrorCode.CONFLICT, f"Already exists: {exc}") from exc
    return _to_resp(contract)


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(tool_id: str, kernel=Depends(get_kernel)):
    try: return _to_resp(kernel.tools.get(tool_id))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Tool {tool_id!r} not found")


@router.delete("/{tool_id}", response_model=dict)
async def delete_tool(tool_id: str, kernel=Depends(get_kernel)):
    try: kernel.tools.unregister(tool_id)
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Tool {tool_id!r} not found")
    return {"deleted": tool_id}
