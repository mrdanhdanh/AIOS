"""Tests for AIOS Dashboard 1.0 observability views (TASK-072)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from aios.autonomy_governor.governor import AutonomyGovernor
from aios.core.healthcheck import HealthCheck
from aios.dashboard.observability_views import (
    DashboardAuthError,
    DashboardViewType,
    ObservabilityDashboard,
    ReadOnlyViolation,
)
from aios.governance.evidence.store import (
    Artifact,
    EvidenceStore,
    Requirement,
    Run,
    TaskRecord,
)
from aios.security.auth import AuthValidator, TokenRecord
from aios.security.secrets import SecretStore


@dataclass
class StubSource:
    """A read-only source used to feed GOALS / ALERTS views in tests."""

    name: str = "stub"
    _items: List[Dict[str, Any]] = field(default_factory=list)

    def list_items(self) -> List[Dict[str, Any]]:
        return [dict(i) for i in self._items]


def _auth() -> AuthValidator:
    av = AuthValidator()
    av.register_token("good-token", TokenRecord(subject="tester", scopes=["dashboard:read"]))
    return av


def _health_check() -> HealthCheck:
    hc = HealthCheck()
    hc.register("db", lambda: None)  # healthy

    def down() -> None:
        raise RuntimeError("connection refused")

    hc.register("cache", down)  # unhealthy (non-critical -> DEGRADED)
    return hc


def _evidence_store() -> EvidenceStore:
    store = EvidenceStore()
    store.add_requirement(Requirement("R1", "title"))
    store.add_task_record(TaskRecord("T1", "R1"))
    store.add_artifact(Artifact("A1", "T1", "R1"))
    store.add_run(Run("RUN1", "A1", "T1", "pytest"))
    store.add_evidence("E1", "T1", "RUN1", "test", "unit", "test_evidence.py", content="ok")
    return store


class TestHealthView:
    def test_aggregates_probes(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth(), health_check=_health_check())
        view = dash.build_view(DashboardViewType.HEALTH, "good-token")
        assert view.view == DashboardViewType.HEALTH
        assert view.data_source == "aios.core.healthcheck"
        names = {i["id"] for i in view.items}
        assert names == {"db", "cache"}
        db = next(i for i in view.items if i["id"] == "db")
        cache = next(i for i in view.items if i["id"] == "cache")
        assert db["status"] == "healthy"
        assert cache["status"] == "unhealthy"
        # Every item carries evidence_ref + provenance.
        assert db["evidence_ref"] == "health:db"
        assert db["provenance"] == {"source": "aios.core.healthcheck"}


class TestReadOnly:
    def test_mutate_state_blocked(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth())
        try:
            dash.mutate_state()
            assert False, "expected ReadOnlyViolation"
        except ReadOnlyViolation:
            pass

    def test_apply_action_blocked(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth())
        try:
            dash.apply_action("kill_switch")
            assert False, "expected ReadOnlyViolation"
        except ReadOnlyViolation:
            pass


class TestAuthRequired:
    def test_missing_token_blocked(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth())
        try:
            dash.build_view(DashboardViewType.HEALTH, None)
            assert False, "expected DashboardAuthError"
        except DashboardAuthError:
            pass

    def test_invalid_token_blocked(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth())
        try:
            dash.build_view(DashboardViewType.HEALTH, "wrong")
            assert False, "expected DashboardAuthError"
        except DashboardAuthError:
            pass

    def test_valid_token_allowed(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth(), health_check=_health_check())
        view = dash.build_view(DashboardViewType.HEALTH, "good-token")
        assert view.view == DashboardViewType.HEALTH


class TestEvidenceTraceability:
    def test_provenance_chain_resolved(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth(), evidence_store=_evidence_store())
        view = dash.build_view(DashboardViewType.EVIDENCE, "good-token")
        assert view.view == DashboardViewType.EVIDENCE
        assert len(view.items) == 1
        item = view.items[0]
        assert item["evidence_ref"] == "E1"
        prov = item["provenance"]
        assert prov["run"] == "RUN1"
        assert prov["artifact"] == "A1"
        assert prov["task"] == "T1"
        assert prov["requirement"] == "R1"
        assert prov["complete"] is True


class TestNoSecretLeak:
    def test_secret_value_redacted(self) -> None:
        src = StubSource(name="goals_source", _items=[
            {"id": "g1", "label": "goal", "status": "active", "value": "api_key=SUPERSECRET123"},
        ])
        dash = ObservabilityDashboard(auth_validator=_auth(), goals_source=src)
        rendered = dash.render(DashboardViewType.GOALS, "good-token")
        flat = str(rendered)
        assert "SUPERSECRET123" not in flat
        assert "api_key=<REDACTED>" in flat

    def test_known_secret_redacted_via_store(self) -> None:
        secrets = SecretStore()
        secrets.put("db", "TOPSECRETVALUE")
        src = StubSource(name="alerts_source", _items=[
            {"id": "a1", "label": "alert", "status": "warn", "detail": "db=TOPSECRETVALUE"},
        ])
        dash = ObservabilityDashboard(auth_validator=_auth(), secret_store=secrets, alerts_source=src)
        rendered = dash.render(DashboardViewType.ALERTS, "good-token")
        assert "TOPSECRETVALUE" not in str(rendered)
        assert "<REDACTED>" in str(rendered)


class TestDeterministic:
    def test_same_data_same_render(self) -> None:
        dash = ObservabilityDashboard(
            auth_validator=_auth(),
            health_check=_health_check(),
            evidence_store=_evidence_store(),
            governor=AutonomyGovernor(),
        )
        first = dash.render_all("good-token")
        second = dash.render_all("good-token")
        assert first == second

    def test_render_is_deep_copied(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth(), health_check=_health_check())
        rendered = dash.render(DashboardViewType.HEALTH, "good-token")
        # Mutating the returned dict must not affect the source.
        rendered["items"].append({"id": "injected"})
        again = dash.render(DashboardViewType.HEALTH, "good-token")
        assert len(again["items"]) == len(rendered["items"]) - 1


class TestAutonomyView:
    def test_governor_state_projected(self) -> None:
        dash = ObservabilityDashboard(auth_validator=_auth(), governor=AutonomyGovernor())
        view = dash.build_view(DashboardViewType.AUTONOMY, "good-token")
        assert view.data_source == "aios.autonomy_governor"
        ids = {i["id"] for i in view.items}
        assert ids == {"mode", "budget", "last_decision"}
        for i in view.items:
            assert i["evidence_ref"].startswith("autonomy:")
