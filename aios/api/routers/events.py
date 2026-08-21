"""Events router — /api/v1/events (TASK-017)."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query, Request
from ..deps import get_event_service, get_pagination
from ..errors import ApiError, ErrorCode
from ..events import ALLOWED_EVENTS
from ..schemas import EventPublishRequest, EventResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=PaginatedResponse[EventResponse])
async def list_events(request: Request, pagination: PaginationParams = Depends(get_pagination),
                     event_type: str = Query(default=None), since_sequence: int = Query(default=0, ge=0)):
    svc = request.app.state.event_service
    envelopes = svc.history(event_type=event_type, since_sequence=since_sequence, limit=pagination.page_size * 10)
    total = len(envelopes)
    page = envelopes[pagination.offset:pagination.offset + pagination.limit]
    items = [EventResponse(event_id=e.event_id, event_type=e.event_type, payload=dict(e.payload), timestamp=e.timestamp, source=e.source) for e in page]
    return PaginatedResponse[EventResponse](items=items, total=total, page=pagination.page, page_size=pagination.page_size, has_next=pagination.offset + pagination.limit < total)


@router.post("", response_model=EventResponse, status_code=201)
async def publish_event(body: EventPublishRequest, request: Request):
    if body.event_type not in ALLOWED_EVENTS:
        raise ApiError(ErrorCode.CONTRACT_INVALID, f"Event type {body.event_type!r} not in whitelist")
    svc = request.app.state.event_service
    env = svc.publish(body.event_type, body.payload, source=body.source)
    return EventResponse(event_id=env.event_id, event_type=env.event_type, payload=dict(env.payload), timestamp=env.timestamp, source=env.source)


@router.get("/types", response_model=dict)
async def list_event_types():
    return {"allowed_events": sorted(ALLOWED_EVENTS)}


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, request: Request):
    for env in request.app.state.event_service.history(limit=10000):
        if env.event_id == event_id:
            return EventResponse(event_id=env.event_id, event_type=env.event_type, payload=dict(env.payload), timestamp=env.timestamp, source=env.source)
    raise ApiError(ErrorCode.NOT_FOUND, f"Event {event_id!r} not found")
