"""Skills router — /api/v1/skills (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from aios.skill.contracts import SkillContract, SkillDependency
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import PaginatedResponse, PaginationParams, SkillCreateRequest, SkillResponse

router = APIRouter(prefix="/skills", tags=["skills"])


def _to_resp(c) -> SkillResponse:
    status = c.status.value if hasattr(c.status, "value") else str(c.status)
    return SkillResponse(skill_id=c.skill_id, name=c.name, version=c.version, description=c.description,
        author=c.author, status=status, enabled=c.enabled, required_capabilities=list(c.required_capabilities))


@router.get("", response_model=PaginatedResponse[SkillResponse])
async def list_skills(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination), q: str = Query(default=None)):
    contracts = kernel.skills.find(q) if q else kernel.skills.list()
    total = len(contracts)
    page = contracts[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[SkillResponse](items=[_to_resp(c) for c in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=SkillResponse, status_code=201)
async def create_skill(body: SkillCreateRequest, kernel=Depends(get_kernel)):
    deps = [SkillDependency(skill_id=d.get("skill_id", ""), version_constraint=d.get("version_constraint", "*")) for d in body.dependencies]
    contract = SkillContract.create(skill_id=body.skill_id, name=body.name, version=body.version, description=body.description,
        author=body.author, dependencies=deps, required_capabilities=body.required_capabilities, permissions=body.permissions, resources=body.resources, runtime=body.runtime, entrypoint=body.entrypoint)
    try: kernel.skills.register(contract)
    except Exception as exc: raise ApiError(ErrorCode.CONFLICT, f"Already exists: {exc}") from exc
    return _to_resp(contract)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str, kernel=Depends(get_kernel)):
    try: return _to_resp(kernel.skills.get(skill_id))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Skill {skill_id!r} not found")


@router.delete("/{skill_id}", response_model=dict)
async def delete_skill(skill_id: str, kernel=Depends(get_kernel)):
    try: kernel.skills.unregister(skill_id)
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Skill {skill_id!r} not found")
    return {"deleted": skill_id}


@router.post("/{skill_id}/enable", response_model=SkillResponse)
async def enable_skill(skill_id: str, kernel=Depends(get_kernel)):
    try: kernel.skills.enable(skill_id); return _to_resp(kernel.skills.get(skill_id))
    except ApiError: raise
    except Exception as exc: raise ApiError(ErrorCode.NOT_FOUND, f"Skill {skill_id!r} not found") from exc


@router.post("/{skill_id}/disable", response_model=SkillResponse)
async def disable_skill(skill_id: str, kernel=Depends(get_kernel)):
    try: kernel.skills.disable(skill_id); return _to_resp(kernel.skills.get(skill_id))
    except ApiError: raise
    except Exception as exc: raise ApiError(ErrorCode.NOT_FOUND, f"Skill {skill_id!r} not found") from exc
