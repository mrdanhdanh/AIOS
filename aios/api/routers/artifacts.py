"""Artifacts router — /api/v1/artifacts (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from aios.runtime.artifact import Artifact
from ..deps import get_kernel, get_pagination
from ..errors import ApiError, ErrorCode
from ..schemas import ArtifactCreateRequest, ArtifactResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def _to_resp(a) -> ArtifactResponse:
    return ArtifactResponse(artifact_id=a.artifact_id, name=a.name, content_type=a.content_type, version=a.version,
        checksum=a.checksum, created_at=a.created_at, metadata=dict(a.metadata))


@router.get("", response_model=PaginatedResponse[ArtifactResponse])
async def list_artifacts(kernel=Depends(get_kernel), pagination: PaginationParams = Depends(get_pagination), name: str = Query(default=None)):
    try: all_arts = list(kernel.artifacts._store.values())
    except AttributeError: all_arts = []
    if name: all_arts = [a for a in all_arts if a.name == name]
    all_arts = sorted(all_arts, key=lambda a: a.artifact_id)
    total = len(all_arts)
    page = all_arts[pagination.offset:pagination.offset + pagination.limit]
    return PaginatedResponse[ArtifactResponse](items=[_to_resp(a) for a in page], total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=ArtifactResponse, status_code=201)
async def create_artifact(body: ArtifactCreateRequest, kernel=Depends(get_kernel)):
    artifact = Artifact.create(name=body.name, content=body.content, content_type=body.content_type, version=body.version, metadata=body.metadata)
    try: kernel.artifacts.put(artifact)
    except Exception as exc: raise ApiError(ErrorCode.CONFLICT, f"Conflict: {exc}") from exc
    return _to_resp(artifact)


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, kernel=Depends(get_kernel)):
    try: return _to_resp(kernel.artifacts.get(artifact_id))
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Artifact {artifact_id!r} not found")


@router.get("/{artifact_id}/content", response_model=dict)
async def get_artifact_content(artifact_id: str, kernel=Depends(get_kernel)):
    try: a = kernel.artifacts.get(artifact_id)
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Artifact {artifact_id!r} not found")
    content = a.content.decode("utf-8") if isinstance(a.content, bytes) else str(a.content)
    return {"artifact_id": a.artifact_id, "content": content, "checksum": a.checksum, "verified": a.verify()}


@router.delete("/{artifact_id}", response_model=dict)
async def delete_artifact(artifact_id: str, kernel=Depends(get_kernel)):
    try: kernel.artifacts.get(artifact_id); kernel.artifacts.delete(artifact_id)
    except ApiError: raise
    except Exception: raise ApiError(ErrorCode.NOT_FOUND, f"Artifact {artifact_id!r} not found")
    return {"deleted": artifact_id}
