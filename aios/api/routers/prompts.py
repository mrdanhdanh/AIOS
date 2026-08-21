"""Prompts router — /api/v1/prompts (TASK-017)."""
from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query
from aios.capability.prompt import PromptContract
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import PaginatedResponse, PaginationParams, PromptCreateRequest, PromptResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


def _to_resp(c) -> PromptResponse:
    return PromptResponse(prompt_id=c.prompt_id, version=c.version, template=c.template, variables=list(c.variables), description=c.description)


@router.get("", response_model=PaginatedResponse[PromptResponse])
async def list_prompts(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination), q: str = Query(default=None)):
    contracts = kernel.prompts.find(q) if q else kernel.prompts.list()
    total = len(contracts)
    page = contracts[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[PromptResponse](items=[_to_resp(c) for c in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=PromptResponse, status_code=201)
async def create_prompt(body: PromptCreateRequest, kernel=Depends(get_kernel)):
    contract = PromptContract.create(prompt_id=body.prompt_id, template=body.template, version=body.version, description=body.description)
    try: kernel.prompts.register(contract)
    except Exception as exc: raise ApiError(ErrorCode.CONFLICT, f"Already exists: {exc}") from exc
    return _to_resp(contract)


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str, kernel=Depends(get_kernel)):
    try: return _to_resp(kernel.prompts.get(prompt_id))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Prompt {prompt_id!r} not found")


@router.delete("/{prompt_id}", response_model=dict)
async def delete_prompt(prompt_id: str, kernel=Depends(get_kernel)):
    try: kernel.prompts.remove(prompt_id)
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Prompt {prompt_id!r} not found")
    return {"deleted": prompt_id}


@router.post("/{prompt_id}/render", response_model=dict)
async def render_prompt(prompt_id: str, body: Dict[str, Any], kernel=Depends(get_kernel)):
    try: return {"prompt_id": prompt_id, "rendered": kernel.prompts.render(prompt_id, **body)}
    except Exception as exc:
        if "not found" in str(exc).lower(): raise ApiError(ErrorCode.NOT_FOUND, f"Prompt {prompt_id!r} not found") from exc
        raise ApiError(ErrorCode.CONTRACT_INVALID, f"Render failed: {exc}") from exc
