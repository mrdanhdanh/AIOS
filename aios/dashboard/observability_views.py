"""AIOS Dashboard 1.0 — observability views (TASK-072).

Read-only operational dashboard. Builds view data from read-only sources
(``aios.core.healthcheck``, ``aios.observability``, ``aios.autonomy_governor``,
``aios.governance.evidence``). Every view is **fail-closed read-only**: any
mutating action raises :class:`ReadOnlyViolation`. Access requires
authentication (reuses ``aios.security.auth``). Secret values are redacted from
view data (reuses ``aios.security.secrets``).

This module is an *observability UI data layer*, not a control plane. It never
imports ``aios.agents`` and never mutates runtime/autonomy/evidence state.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from aios.autonomy_governor.governor import AutonomyGovernor
from aios.core.healthcheck import HealthCheck, HealthStatus
from aios.governance.evidence.store import EvidenceStore
from aios.observability.health_api import HealthAPI
from aios.observability.metrics import MetricsCollector
from aios.security.auth import AuthError, AuthValidator
from aios.security.context import SecurityContext
from aios.security.secrets import SecretStore, redact_message


class DashboardViewType(str, Enum):
    """The five canonical Dashboard 1.0 views."""

    HEALTH = "health"
    GOALS = "goals"
    AUTONOMY = "autonomy"
    EVIDENCE = "evidence"
    ALERTS = "alerts"

    @classmethod
    def all(cls) -> List["DashboardViewType"]:
        return [cls.HEALTH, cls.GOALS, cls.AUTONOMY, cls.EVIDENCE, cls.ALERTS]


class ReadOnlyViolation(Exception):
    """Raised when a mutating action is attempted through the read-only dashboard.

    The dashboard is an observability surface only. Any attempt to change state
    (kill switch, policy change, write, etc.) must go through the API/CLI with
    auth — never through the dashboard. Fail-closed.
    """


class DashboardAuthError(Exception):
    """Raised when dashboard access is attempted without valid authentication.

    Fail-closed: missing / unknown / expired tokens are rejected.
    """


class ReadOnlySource(Protocol):
    """A read-only provider of dashboard items (goals / alerts / custom)."""

    name: str

    def list_items(self) -> List[Dict[str, Any]]:
        """Return a list of item dicts. Must not mutate any backing state."""
        ...


@dataclass
class _EmptySource:
    """Default no-op read-only source (yields no items)."""

    name: str = "empty"

    def list_items(self) -> List[Dict[str, Any]]:
        return []


@dataclass
class DashboardView:
    """A single read-only dashboard view.

    Fields
    ------
    view
        One of :class:`DashboardViewType`.
    data_source
        Identifier of the read-only source this view was projected from.
    refresh
        Deterministic refresh strategy (e.g. ``"manual"``, ``"poll:30s"``).
    evidence_ref
        Top-level evidence reference for the whole view.
    items
        List of view items; every item carries ``evidence_ref`` + ``provenance``.
    summary
        Aggregated summary values for the view.
    """

    view: DashboardViewType
    data_source: str = "unknown"
    refresh: str = "manual"
    evidence_ref: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "view": self.view.value,
            "data_source": self.data_source,
            "read_only": True,
            "refresh": self.refresh,
            "evidence_ref": self.evidence_ref,
            "items": self.items,
            "summary": self.summary,
        }


def _item(
    item_id: str,
    label: str,
    status: str,
    evidence_ref: str,
    provenance: Dict[str, Any],
    **extra: Any,
) -> Dict[str, Any]:
    """Build a view item that always carries evidence_ref + provenance."""
    item: Dict[str, Any] = {
        "id": item_id,
        "label": label,
        "status": status,
        "evidence_ref": evidence_ref,
        "provenance": provenance,
    }
    item.update(extra)
    return item


class ObservabilityDashboard:
    """Builds read-only Dashboard 1.0 views from live sources.

    All sources are injected (dependency injection) so the builder stays a pure
    projection. By default it wires the canonical AIOS surfaces; callers may
    substitute mock/stub sources for testing.
    """

    def __init__(
        self,
        *,
        auth_validator: Optional[AuthValidator] = None,
        secret_store: Optional[SecretStore] = None,
        health_check: Optional[HealthCheck] = None,
        health_api: Optional[HealthAPI] = None,
        metrics: Optional[MetricsCollector] = None,
        governor: Optional[AutonomyGovernor] = None,
        evidence_store: Optional[EvidenceStore] = None,
        goals_source: Optional[ReadOnlySource] = None,
        alerts_source: Optional[ReadOnlySource] = None,
        read_only: bool = True,
    ) -> None:
        self._auth = auth_validator or AuthValidator()
        self._secrets = secret_store or SecretStore()
        self._health = health_check
        self._health_api = health_api
        self._metrics = metrics
        self._governor = governor
        self._evidence = evidence_store
        self._goals = goals_source or _EmptySource()
        self._alerts = alerts_source or _EmptySource()
        self._read_only = read_only
        self._builders = {
            DashboardViewType.HEALTH: self._build_health,
            DashboardViewType.GOALS: self._build_goals,
            DashboardViewType.AUTONOMY: self._build_autonomy,
            DashboardViewType.EVIDENCE: self._build_evidence,
            DashboardViewType.ALERTS: self._build_alerts,
        }

    # ── Auth (fail-closed) ──────────────────────────────────────────────
    def require_auth(self, token: Optional[str]) -> SecurityContext:
        """Validate the caller's token. Raises :class:`DashboardAuthError` if missing/invalid."""
        try:
            return self._auth.validate(token)
        except AuthError as exc:
            raise DashboardAuthError(str(exc)) from exc

    # ── Read-only enforcement (fail-closed) ─────────────────────────────
    def mutate_state(self, *args: Any, **kwargs: Any) -> None:
        """Any mutating action through the dashboard is rejected (read-only)."""
        raise ReadOnlyViolation(
            "dashboard is read-only; mutate state only via the API/CLI with auth"
        )

    def apply_action(self, action: str, token: Optional[str] = None, **kwargs: Any) -> None:
        """Alias for :meth:`mutate_state` — actions go through the control plane."""
        raise ReadOnlyViolation(
            f"action '{action}' is not permitted via the dashboard; use the API/CLI"
        )

    def _ensure_read_only(self) -> None:
        if not self._read_only:
            raise ReadOnlyViolation("dashboard read-only mode is disabled")

    # ── View builders ───────────────────────────────────────────────────
    def build_view(
        self,
        view: "DashboardViewType | str",
        token: Optional[str],
        *,
        refresh: str = "manual",
    ) -> DashboardView:
        """Build a single view. Requires auth; fails closed on missing token."""
        self.require_auth(token)  # BLOCK unauthenticated access
        self._ensure_read_only()
        if isinstance(view, str):
            view = DashboardViewType(view)
        if view not in self._builders:
            raise ValueError(f"unknown dashboard view: {view}")
        built = self._builders[view]()
        built.refresh = refresh
        return built

    def render(
        self,
        view: "DashboardViewType | str",
        token: Optional[str],
        *,
        refresh: str = "manual",
    ) -> Dict[str, Any]:
        """Build a view and return a redacted, deterministic dict."""
        built = self.build_view(view, token, refresh=refresh)
        data = copy.deepcopy(built.to_dict())
        return self._redact(data)

    def render_all(self, token: Optional[str], *, refresh: str = "manual") -> Dict[str, Dict[str, Any]]:
        """Render every view behind a single auth check (deterministic)."""
        self.require_auth(token)
        self._ensure_read_only()
        out: Dict[str, Dict[str, Any]] = {}
        for vt in DashboardViewType.all():
            built = self._builders[vt]()
            built.refresh = refresh
            out[vt.value] = self._redact(copy.deepcopy(built.to_dict()))
        return out

    # ── Source projections ──────────────────────────────────────────────
    def _build_health(self) -> DashboardView:
        items: List[Dict[str, Any]] = []
        source = "aios.core.healthcheck"
        summary: Dict[str, Any] = {"status": "unknown"}
        if self._health_api is not None:
            source = "aios.observability.health_api"
            system = self._health_api.get_health()
            d = system.to_dict()
            for comp in d.get("components", []):
                name = comp.get("name", "component")
                items.append(
                    _item(
                        name,
                        name,
                        str(comp.get("status", "unknown")),
                        f"health:{name}",
                        {"source": source},
                        detail=comp.get("detail", ""),
                    )
                )
            summary = {
                "overall": d.get("overall"),
                "violations": len(d.get("violations", [])),
            }
        elif self._health is not None:
            result = self._health.run()
            for probe in result.probes:
                items.append(
                    _item(
                        probe.name,
                        probe.name,
                        "healthy" if probe.healthy else "unhealthy",
                        f"health:{probe.name}",
                        {"source": source},
                        message=probe.message,
                    )
                )
            summary = {"status": result.status.value}
        if self._metrics is not None:
            snap = self._metrics.snapshot()
            # Deterministic subset — timestamp excluded on purpose.
            summary["metrics"] = {
                "execution_count": snap.execution_count,
                "execution_success": snap.execution_success,
                "execution_failure": snap.execution_failure,
                "model_calls": snap.model_calls,
                "model_tokens": snap.model_tokens,
                "model_cost": snap.model_cost,
                "resource_cpu": snap.resource_cpu,
                "resource_memory_mb": snap.resource_memory_mb,
            }
        return DashboardView(
            view=DashboardViewType.HEALTH,
            data_source=source,
            refresh="manual",
            evidence_ref="health:summary",
            items=items,
            summary=summary,
        )

    def _build_goals(self) -> DashboardView:
        items = [
            self._tag_source(it, "goals") for it in self._goals.list_items()
        ]
        return DashboardView(
            view=DashboardViewType.GOALS,
            data_source=getattr(self._goals, "name", "goals_source"),
            refresh="manual",
            evidence_ref="goals:summary",
            items=items,
            summary={"count": len(items)},
        )

    def _build_autonomy(self) -> DashboardView:
        items: List[Dict[str, Any]] = []
        source = "aios.autonomy_governor"
        summary: Dict[str, Any] = {"mode": "unknown"}
        if self._governor is not None:
            st = self._governor.state()
            items.append(
                _item(
                    "mode", "mode", st["mode"], "autonomy:mode",
                    {"source": source}, value=st["mode"],
                )
            )
            items.append(
                _item(
                    "budget", "budget", "ok", "autonomy:budget",
                    {"source": source}, value=st["budget"],
                )
            )
            items.append(
                _item(
                    "last_decision", "last_decision", "ok", "autonomy:last_decision",
                    {"source": source}, value=st["last_reason"],
                )
            )
            summary = {"mode": st["mode"], "last_reason": st["last_reason"]}
        return DashboardView(
            view=DashboardViewType.AUTONOMY,
            data_source=source,
            refresh="manual",
            evidence_ref="autonomy:state",
            items=items,
            summary=summary,
        )

    def _build_evidence(self) -> DashboardView:
        items: List[Dict[str, Any]] = []
        source = "aios.governance.evidence"
        if self._evidence is not None:
            for ev in self._evidence.list_all():
                chain = self._evidence.get_provenance_chain(ev.evidence_id)
                items.append(
                    {
                        "id": ev.evidence_id,
                        "task_id": ev.task_id,
                        "type": ev.type,
                        "source": ev.source,
                        "content_hash": ev.content_hash,
                        "status": ev.status,
                        "evidence_ref": ev.evidence_id,
                        "provenance": {
                            "run": chain.run.run_id if chain.run else None,
                            "artifact": chain.artifact.artifact_id if chain.artifact else None,
                            "task": chain.task.task_id if chain.task else None,
                            "requirement": (
                                chain.requirement.requirement_id
                                if chain.requirement
                                else None
                            ),
                            "complete": chain.complete,
                        },
                    }
                )
        return DashboardView(
            view=DashboardViewType.EVIDENCE,
            data_source=source,
            refresh="manual",
            evidence_ref="governance.evidence:store",
            items=items,
            summary={"count": len(items)},
        )

    def _build_alerts(self) -> DashboardView:
        items = [
            self._tag_source(it, "alerts") for it in self._alerts.list_items()
        ]
        return DashboardView(
            view=DashboardViewType.ALERTS,
            data_source=getattr(self._alerts, "name", "alerts_source"),
            refresh="manual",
            evidence_ref="alerts:summary",
            items=items,
            summary={"count": len(items)},
        )

    # ── Helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _tag_source(it: Dict[str, Any], kind: str) -> Dict[str, Any]:
        """Ensure an injected item carries evidence_ref + provenance."""
        item = dict(it)
        item.setdefault("evidence_ref", f"{kind}:{item.get('id', 'item')}")
        item.setdefault("provenance", {"source": f"{kind}_source"})
        return item

    def _redact(self, data: Any) -> Any:
        """Recursively redact secret values from view data (reuses aios.security)."""
        if isinstance(data, str):
            text = redact_message(data)
            if self._secrets is not None:
                text = self._secrets.redact(text)
            return text
        if isinstance(data, dict):
            return {k: self._redact(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._redact(v) for v in data]
        return data


def default_dashboard() -> ObservabilityDashboard:
    """Construct a dashboard wired to the canonical AIOS read-only surfaces.

    Auth is fail-closed: no tokens are registered, so all access is BLOCKed
    until a token is registered on ``dashboard.require_auth``'s validator.
    """
    return ObservabilityDashboard(
        health_api=HealthAPI(),
        metrics=MetricsCollector(),
        governor=AutonomyGovernor(),
        evidence_store=EvidenceStore(),
    )
