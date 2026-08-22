"""FastAPI bridge for AIOS Dashboard 1.0 (TASK-072).

Exposes the read-only observability views behind authentication. FastAPI and
``aios.api`` are imported lazily inside :func:`create_dashboard_router` so the
dashboard data layer stays importable without the API extra installed.

This is a presentation boundary only — it delegates to
:class:`~aios.dashboard.observability_views.ObservabilityDashboard`, which
enforces read-only + auth + redaction. No business logic lives here.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from aios.dashboard.observability_views import (
    DashboardAuthError,
    DashboardViewType,
    ObservabilityDashboard,
)


def create_dashboard_router(
    dashboard: ObservabilityDashboard,
    *,
    prefix: str = "/dashboard",
) -> Any:
    """Build a FastAPI router exposing the five dashboard views behind auth.

    The router reads the bearer/API-key token from the request and forwards it
    to ``dashboard.render``, which fails closed on missing/invalid auth.
    """
    from fastapi import APIRouter, Depends, Header, HTTPException

    router = APIRouter(prefix=prefix, tags=["dashboard"])

    def _extract_token(
        authorization: Optional[str] = Header(default=None, alias="Authorization"),
        x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    ) -> str:
        if authorization:
            # Accept "Bearer <token>" or raw "<token>".
            return authorization.split(" ", 1)[1] if " " in authorization else authorization
        return x_api_key or ""

    @router.get("")
    @router.get("/")
    def list_views(token: str = Depends(_extract_token)) -> Dict[str, Any]:
        try:
            return {
                "views": [v.value for v in DashboardViewType.all()],
                "read_only": True,
            }
        except DashboardAuthError as exc:  # pragma: no cover - list is pre-auth
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.get("/{view}")
    def get_view(view: str, token: str = Depends(_extract_token)) -> Dict[str, Any]:
        try:
            return dashboard.render(view, token)
        except DashboardAuthError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return router


def register_dashboard_router(app: Any, dashboard: ObservabilityDashboard, *, prefix: str = "/dashboard") -> None:
    """Mount the dashboard router onto an existing FastAPI app (aios.api)."""
    app.include_router(create_dashboard_router(dashboard, prefix=prefix))
