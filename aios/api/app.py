"""FastAPI application factory — presentation boundary (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from aios.core.config import Config
from aios.core.healthcheck import HealthCheck
from aios.runtime.kernel import RuntimeKernel

from .auth import AuthConfig, configure_auth
from .contracts import API_PREFIX, CURRENT_API_VERSION
from .errors import register_exception_handlers
from .events import EventService
from .websocket import ConnectionManager, WebSocketGateway


def create_app(
    kernel: Optional[RuntimeKernel] = None,
    config: Optional[Config] = None,
    auth_config: Optional[AuthConfig] = None,
    event_service: Optional[EventService] = None,
    gateway: Optional[WebSocketGateway] = None,
) -> FastAPI:
    cfg = config or Config()
    kern = kernel or RuntimeKernel()
    configure_auth(auth_config or AuthConfig())
    svc = event_service or EventService(bus=kern.bus)
    gw = gateway or WebSocketGateway(event_service=svc)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        gw.start()
        yield
        gw.stop()

    app = FastAPI(
        title="AIOS API", description="AIOS Runtime-First API Boundary",
        version=CURRENT_API_VERSION, lifespan=lifespan,
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=f"{API_PREFIX}/docs", redoc_url=f"{API_PREFIX}/redoc",
    )

    app.state.kernel = kern
    app.state.config = cfg
    app.state.event_service = svc
    app.state.gateway = gw
    app.state.healthcheck = HealthCheck(config=cfg)

    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        response.headers["X-API-Version"] = CURRENT_API_VERSION
        return response

    register_exception_handlers(app)

    # Import and include all 15 routers
    from .routers.health import router as health_router
    from .routers.system import router as system_router
    from .routers.orchestrator import router as orch_router
    from .routers.executions import router as exec_router
    from .routers.workflows import router as wf_router
    from .routers.tasks import router as tasks_router
    from .routers.agents import router as agents_router
    from .routers.capabilities import router as caps_router
    from .routers.tools import router as tools_router
    from .routers.skills import router as skills_router
    from .routers.memory import router as mem_router
    from .routers.artifacts import router as arts_router
    from .routers.models import router as models_router
    from .routers.prompts import router as prompts_router
    from .routers.events import router as events_router
    from .routers.independent_harness import router as ih_router
    from .routers.coordinator import router as coord_router
    from .routers.control_center import router as cc_router

    for r in [health_router, system_router, orch_router, exec_router, wf_router,
              tasks_router, agents_router, caps_router, tools_router, skills_router,
              mem_router, arts_router, models_router, prompts_router, events_router,
              ih_router, coord_router, cc_router]:
        app.include_router(r, prefix=API_PREFIX)

    @app.websocket(f"{API_PREFIX}/ws/events")
    async def ws_events(websocket: WebSocket, last_event_id: Optional[str] = Query(default=None)):
        await gw.handle_connection(websocket, last_event_id=last_event_id)

    @app.get("/", tags=["root"])
    async def root():
        return {"name": "AIOS API", "version": CURRENT_API_VERSION, "prefix": API_PREFIX,
                "docs": f"{API_PREFIX}/docs", "openapi": f"{API_PREFIX}/openapi.json"}

    return app
