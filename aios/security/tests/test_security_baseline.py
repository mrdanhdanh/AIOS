"""Tests for the TASK-070 Security Baseline.

Covers every Acceptance Criterion and every row of the Test Matrix:
  * external call without auth            -> BLOCK
  * action without permission             -> BLOCK (fail-closed)
  * secret in log                         -> redacted / blocked
  * scope exceeded                        -> BLOCK (least-privilege)
  * privileged action                     -> audit evidence written
  * same context + action                 -> same decision (deterministic)
Plus integration with Runtime (Permission/Policy), Governor (T054) and API.
"""
from __future__ import annotations

import pytest

from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine

from aios.autonomy_governor.contracts import AutonomyMode, AutonomyPolicy
from aios.autonomy_governor.governor import AutonomyGovernor

from aios.governance.evidence.store import EvidenceStore

from aios.security.auth import AuthError, AuthValidator, TokenRecord
from aios.security.audit import SecurityAudit
from aios.security.broker import SecurityPermissionBroker
from aios.security.context import SecurityContext
from aios.security.engine import SecurityBaseline, SecurityDecision
from aios.security.secrets import SecretStore


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _authed_ctx(principal: str = "user1", scopes=None, permissions=None) -> SecurityContext:
    return SecurityContext(
        principal=principal,
        scopes=list(scopes or []),
        permissions=dict(permissions or {}),
        authenticated=True,
    )


def _broker_with(principal: str, target: str, action: str) -> SecurityPermissionBroker:
    broker = PermissionBroker()
    broker.grant(principal, Permission(SecurityPermissionBroker._scope_for(action), target))
    return SecurityPermissionBroker(broker=broker)


# --------------------------------------------------------------------------- #
# AC1 / Test Matrix: external call without auth -> BLOCK
# --------------------------------------------------------------------------- #
class TestExternalAuth:
    def test_missing_token_raises(self):
        engine = SecurityBaseline(require_auth=True)
        with pytest.raises(AuthError):
            engine.authenticate(None)

    def test_unauthenticated_context_blocked(self):
        engine = SecurityBaseline(require_auth=True)
        ctx = SecurityContext(principal="anon", authenticated=False)
        decision = engine.check(ctx, "cap:x", "capability_invoke")
        assert decision.blocked
        assert "authentication" in decision.reason.lower()

    def test_valid_token_authenticates(self):
        auth = AuthValidator()
        auth.register_token(
            "tok-123",
            TokenRecord(subject="svc", scopes=["read"], permissions={"cap:r": ["read"]}),
        )
        engine = SecurityBaseline(auth=auth, require_auth=True)
        ctx = engine.authenticate("tok-123")
        assert ctx.authenticated and ctx.principal == "svc"


# --------------------------------------------------------------------------- #
# AC2 / Test Matrix: action without permission -> BLOCK (fail-closed)
# --------------------------------------------------------------------------- #
class TestPermissionFailClosed:
    def test_no_grant_blocks(self):
        engine = SecurityBaseline(
            broker=SecurityPermissionBroker(broker=PermissionBroker()),
            require_auth=False,
        )
        decision = engine.check(_authed_ctx(), "cap:weather", "capability_invoke")
        assert decision.blocked
        assert "permission" in decision.reason.lower()

    def test_grant_allows(self):
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:weather", "capability_invoke"),
            require_auth=False,
        )
        decision = engine.check(_authed_ctx(), "cap:weather", "capability_invoke")
        assert decision.allowed

    def test_policy_deny_overrides_grant(self):
        broker = PermissionBroker()
        broker.grant("user1", Permission(PermissionScope.CAPABILITY_INVOKE, "cap:x"))
        policy = PolicyEngine.deny_all(broker=broker)
        engine = SecurityBaseline(
            broker=SecurityPermissionBroker(broker=broker, policy=policy),
            require_auth=False,
        )
        decision = engine.check(_authed_ctx(), "cap:x", "capability_invoke")
        assert decision.blocked


# --------------------------------------------------------------------------- #
# AC3 / Test Matrix: secret in log -> redacted / blocked
# --------------------------------------------------------------------------- #
class TestSecretHandling:
    def test_value_redacted_from_log(self):
        store = SecretStore()
        store.put("db", "supersecretvalue123")
        msg = "connect password=supersecretvalue123 token=abc123def"
        redacted = store.redact(msg)
        assert "supersecretvalue123" not in redacted
        assert "<REDACTED>" in redacted

    def test_pattern_redacted(self):
        msg = "Authorization: Bearer eyJ.abc.def"
        assert "eyJ.abc.def" not in SecretStore().redact(msg)

    def test_context_never_holds_secret_value(self):
        ctx = SecurityContext(
            principal="p", authenticated=True,
            secret_refs={"db": "secret://db/main"},
        )
        serialized = str(ctx.to_dict())
        assert "secret://db/main" in serialized
        assert "supersecretvalue123" not in serialized

    def test_get_ref_excludes_value(self):
        store = SecretStore()
        store.put("db", "supersecretvalue123")
        ref = store.get_ref("db")
        assert ref is not None
        assert "supersecretvalue123" not in repr(ref)


# --------------------------------------------------------------------------- #
# AC4 / Test Matrix: scope exceeded -> BLOCK (least-privilege)
# --------------------------------------------------------------------------- #
class TestLeastPrivilege:
    def test_exceeded_scope_blocked(self):
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:x", "capability_invoke"),
            require_auth=False,
        )
        ctx = _authed_ctx(scopes=["read"])
        decision = engine.check(ctx, "cap:x", "capability_invoke", scope="admin")
        assert decision.blocked
        assert "scope" in decision.reason.lower()

    def test_within_scope_allowed(self):
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:x", "capability_invoke"),
            require_auth=False,
        )
        ctx = _authed_ctx(scopes=["admin"])
        decision = engine.check(ctx, "cap:x", "capability_invoke", scope="admin")
        assert decision.allowed

    def test_wildcard_scope_allowed(self):
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:x", "capability_invoke"),
            require_auth=False,
        )
        ctx = _authed_ctx(scopes=["*"])
        decision = engine.check(ctx, "cap:x", "capability_invoke", scope="admin")
        assert decision.allowed


# --------------------------------------------------------------------------- #
# AC5 / Test Matrix: privileged action -> audit evidence written
# --------------------------------------------------------------------------- #
class TestAuditTrail:
    def test_privileged_action_audited(self):
        audit = SecurityAudit()
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:x", "capability_invoke"),
            audit=audit,
            require_auth=False,
        )
        decision = engine.check(
            _authed_ctx(), "cap:x", "capability_invoke", privileged=True
        )
        assert decision.allowed
        assert decision.evidence_ref is not None
        assert audit.last() is not None
        assert audit.last().decision == "ALLOW"
        assert audit.last().evidence_ref == decision.evidence_ref

    def test_blocked_action_audited(self):
        audit = SecurityAudit()
        engine = SecurityBaseline(
            broker=SecurityPermissionBroker(broker=PermissionBroker()),
            audit=audit,
            require_auth=False,
        )
        engine.check(_authed_ctx(), "cap:x", "capability_invoke")
        assert audit.last() is not None
        assert audit.last().decision == "BLOCK"

    def test_audit_uses_evidence_store(self):
        store = EvidenceStore()
        audit = SecurityAudit(evidence_store=store, task_id="TASK-070")
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:x", "capability_invoke"),
            audit=audit,
            require_auth=False,
        )
        decision = engine.check(
            _authed_ctx(), "cap:x", "capability_invoke", privileged=True
        )
        assert decision.evidence_ref is not None
        ev = store.get(decision.evidence_ref)
        assert ev.task_id == "TASK-070"
        assert ev.type == "security_audit"


# --------------------------------------------------------------------------- #
# AC6 / Test Matrix: same context + action -> same decision (deterministic)
# --------------------------------------------------------------------------- #
class TestDeterminism:
    def test_same_inputs_same_decision(self):
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:x", "capability_invoke"),
            require_auth=False,
        )
        ctx = _authed_ctx()
        d1 = engine.check(ctx, "cap:x", "capability_invoke")
        d2 = engine.check(ctx, "cap:x", "capability_invoke")
        assert d1.allowed == d2.allowed
        assert d1.reason == d2.reason

    def test_deterministic_block(self):
        engine = SecurityBaseline(
            broker=SecurityPermissionBroker(broker=PermissionBroker()),
            require_auth=False,
        )
        ctx = _authed_ctx()
        d1 = engine.check(ctx, "cap:x", "capability_invoke")
        d2 = engine.check(ctx, "cap:x", "capability_invoke")
        assert d1.blocked and d2.blocked
        assert d1.reason == d2.reason


# --------------------------------------------------------------------------- #
# AC7: integration with Runtime (Permission/Policy) + Governor (T054) + API
# --------------------------------------------------------------------------- #
class TestIntegration:
    def test_governor_scope_enforced(self):
        governor = AutonomyGovernor(policy=AutonomyPolicy(mode=AutonomyMode.BOUNDED))
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:blocked", "capability_invoke"),
            governor=governor,
            require_auth=False,
        )
        # ctx scoped to "cap:allowed" only -> target "cap:blocked" blocked by governor
        ctx = _authed_ctx(scopes=["cap:allowed"])
        decision = engine.check(ctx, "cap:blocked", "capability_invoke")
        assert decision.blocked
        assert "governor" in decision.reason.lower()

    def test_governor_scope_allows(self):
        governor = AutonomyGovernor(policy=AutonomyPolicy(mode=AutonomyMode.BOUNDED))
        engine = SecurityBaseline(
            broker=_broker_with("user1", "cap:allowed", "capability_invoke"),
            governor=governor,
            require_auth=False,
        )
        ctx = _authed_ctx(scopes=["cap:allowed"])
        decision = engine.check(ctx, "cap:allowed", "capability_invoke")
        assert decision.allowed

    def test_api_bridge_builds_context(self):
        fastapi = pytest.importorskip("fastapi")
        from aios.api.auth import AuthContext
        from aios.security.api_bridge import from_api_context

        auth_ctx = AuthContext(subject="svc", authenticated=True)
        ctx = from_api_context(auth_ctx, scopes=["read"])
        assert ctx.principal == "svc"
        assert ctx.authenticated
        assert "read" in ctx.scopes

    def test_api_bridge_rejects_wrong_type(self):
        pytest.importorskip("fastapi")
        from aios.security.api_bridge import from_api_context

        with pytest.raises(TypeError):
            from_api_context(object())
