"""Memory router — /api/v1/memory (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from aios.runtime.memory import MemoryEntry, MemoryType
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import MemoryCreateRequest, MemoryResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/memory", tags=["memory"])


def _to_resp(e) -> MemoryResponse:
    return MemoryResponse(entry_id=e.entry_id, memory_type=e.memory_type.value if hasattr(e.memory_type, "value") else str(e.memory_type),
        scope_id=e.scope_id, content=e.content, content_hash=e.content_hash, producer=e.producer, source=e.source,
        status=e.status.value if hasattr(e.status, "value") else str(e.status), created_at=e.created_at, metadata=dict(e.metadata))


@router.get("", response_model=PaginatedResponse[MemoryResponse])
async def list_memory(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination),
                      memory_type: str = Query(default=None), scope_id: str = Query(default=None), q: str = Query(default=None)):
    store = kernel.memory
    if q: entries = store.search(q, scope_id=scope_id)
    elif memory_type:
        try: entries = [e for e in store.list_by_type(MemoryType(memory_type)) if not scope_id or e.scope_id == scope_id]
        except ValueError: raise ApiError(ErrorCode.INVALID_REQUEST, f"Invalid memory_type {memory_type!r}")
    elif scope_id: entries = store.list_by_scope(scope_id)
    else: entries = store.list_active()
    total = len(entries)
    page = entries[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[MemoryResponse](items=[_to_resp(e) for e in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(body: MemoryCreateRequest, kernel=Depends(get_kernel)):
    try: mt = MemoryType(body.memory_type)
    except ValueError as exc: raise ApiError(ErrorCode.CONTRACT_INVALID, f"Invalid memory_type: {exc}") from exc
    entry = MemoryEntry.create(memory_type=mt, scope_id=body.scope_id, content=body.content,
        producer=body.producer, source=body.source, task_id=body.task_id, run_id=body.run_id, metadata=body.metadata)
    try: kernel.memory.put(entry)
    except Exception as exc: raise ApiError(ErrorCode.CONFLICT, f"Conflict: {exc}") from exc
    return _to_resp(entry)


@router.get("/{entry_id}", response_model=MemoryResponse)
async def get_memory(entry_id: str, kernel=Depends(get_kernel)):
    try: return _to_resp(kernel.memory.get(entry_id))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Memory {entry_id!r} not found")


@router.delete("/{entry_id}", response_model=dict)
async def delete_memory(entry_id: str, kernel=Depends(get_kernel)):
    try: kernel.memory.get(entry_id); kernel.memory.delete(entry_id)
    except ApiError: raise
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Memory {entry_id!r} not found")
    return {"deleted": entry_id}
