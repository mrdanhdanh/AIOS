"""Models router — /api/v1/models (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import ModelResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=PaginatedResponse[ModelResponse])
async def list_models(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination)):
    try:
        from aios.runtime.providers.registry import ProviderRegistry
        registry = kernel.container.resolve(ProviderRegistry)
        models = registry.list_models()
    except Exception:
        models = []
    total = len(models)
    page = models[pagination.offset:pagination.offset + pagination.limit]
    items = []
    for m in page:
        caps = [c.value if hasattr(c, "value") else str(c) for c in getattr(m, "capabilities", [])]
        items.append(ModelResponse(model_id=m.model_id, provider=m.provider, display_name=getattr(m, "display_name", m.model_id),
            capabilities=caps, offline=getattr(m, "offline", False), cost_per_1k_input=getattr(m, "cost_per_1k_input", 0.0),
            cost_per_1k_output=getattr(m, "cost_per_1k_output", 0.0)))
    return PaginatedResponse[ModelResponse](items=items, total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str, kernel=Depends(get_kernel)):
    try:
        from aios.runtime.providers.registry import ProviderRegistry
        m = kernel.container.resolve(ProviderRegistry).get_model(model_id)
        caps = [c.value if hasattr(c, "value") else str(c) for c in getattr(m, "capabilities", [])]
        return ModelResponse(model_id=m.model_id, provider=m.provider, display_name=getattr(m, "display_name", m.model_id),
            capabilities=caps, offline=getattr(m, "offline", False), cost_per_1k_input=getattr(m, "cost_per_1k_input", 0.0),
            cost_per_1k_output=getattr(m, "cost_per_1k_output", 0.0))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Model {model_id!r} not found")
