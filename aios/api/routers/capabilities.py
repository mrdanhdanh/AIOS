"""Capabilities router — /api/v1/capabilities (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from aios.capability.capability import CapabilityContract
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import CapabilityCreateRequest, CapabilityResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


def _to_resp(c) -> CapabilityResponse:
    return CapabilityResponse(capability_id=c.capability_id, version=c.version, description=c.description,
        permissions=list(c.permissions), resources=dict(c.resources), tags=list(c.tags))


@router.get("", response_model=PaginatedResponse[CapabilityResponse])
async def list_capabilities(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination), q: str = Query(default=None)):
    contracts = kernel.capabilities.find(q) if q else kernel.capabilities.list()
    total = len(contracts)
    page = contracts[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[CapabilityResponse](items=[_to_resp(c) for c in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=CapabilityResponse, status_code=201)
async def create_capability(body: CapabilityCreateRequest, kernel=Depends(get_kernel)):
    contract = CapabilityContract.create(capability_id=body.capability_id, version=body.version, description=body.description, permissions=body.permissions, resources=body.resources, tags=body.tags)
    try: kernel.capabilities.register(contract)
    except Exception as exc: raise ApiError(ErrorCode.CONFLICT, f"Already exists: {exc}") from exc
    return _to_resp(contract)


@router.get("/{capability_id}", response_model=CapabilityResponse)
async def get_capability(capability_id: str, kernel=Depends(get_kernel)):
    try: return _to_resp(kernel.capabilities.get(capability_id))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Capability {capability_id!r} not found")


@router.delete("/{capability_id}", response_model=dict)
async def delete_capability(capability_id: str, kernel=Depends(get_kernel)):
    try: kernel.capabilities.remove(capability_id)
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Capability {capability_id!r} not found")
    return {"deleted": capability_id}
