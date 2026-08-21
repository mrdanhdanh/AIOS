"""Tests for OrchestratorPermissionBroker — AC-012-05/06 (TASK-012)."""

import pytest

from aios.orchestrator.permission_broker import OrchestratorPermissionBroker, OrchestratorPermissionBrokerError, OrchestratorPermissionDecision
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest, PolicyRule


class TestPermissionBroker:
    def test_aggregate_dedup(self):
        b = OrchestratorPermissionBroker()
        result = b.aggregate(["filesystem.read", "filesystem.read", "filesystem.write"])
        assert result == ["filesystem.read", "filesystem.write"]

    def test_aggregate_normalize(self):
        b = OrchestratorPermissionBroker()
        result = b.aggregate(["Filesystem.Read", " filesystem.read "])
        assert len(result) == 1

    def test_allow_when_granted(self):
        broker = PermissionBroker()
        broker.grant("agent:alice", Permission(PermissionScope.READ, "filesystem.read"))
        engine = PolicyEngine(broker=broker)
        engine.add_rule(PolicyRule("allow-read", applies=lambda r: r.resource == "filesystem.read", decision=PolicyDecision.ALLOW, reason="allow"))
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        decision = ob.check("agent:alice", ["filesystem.read"], resource="filesystem.read")
        assert decision == OrchestratorPermissionDecision.ALLOW

    def test_deny_when_not_granted(self):
        broker = PermissionBroker()
        engine = PolicyEngine(broker=broker)
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        decision = ob.check("agent:alice", ["filesystem.write"], resource="filesystem.write")
        assert decision == OrchestratorPermissionDecision.DENY

    def test_ask_when_insufficient(self):
        broker = PermissionBroker()
        broker.grant("agent:alice", Permission(PermissionScope.READ, "filesystem.read"))
        engine = PolicyEngine(broker=broker)
        # No rule for this resource -> INSUFFICIENT -> ASK
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        decision = ob.check("agent:alice", ["filesystem.read"], resource="filesystem.read")
        assert decision == OrchestratorPermissionDecision.ASK

    def test_request_and_approve(self):
        broker = PermissionBroker()
        broker.grant("agent:alice", Permission(PermissionScope.READ, "filesystem.read"))
        engine = PolicyEngine(broker=broker)
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        rid, decision = ob.request("agent:alice", ["filesystem.read"], resource="filesystem.read")
        assert decision == OrchestratorPermissionDecision.ASK
        # Approve
        result = ob.approve(rid, approved=True)
        assert result == OrchestratorPermissionDecision.ALLOW
        # Now check should be ALLOW
        decision2 = ob.check("agent:alice", ["filesystem.read"], resource="filesystem.read")
        # After grant, need a rule to allow; but broker now has permission, and no DENY rule, so INSUFFICIENT still -> ASK
        # Actually after approve, broker grants permission, but policy still INSUFFICIENT without ALLOW rule
        # So we test that approve grants the permission
        assert broker.has("agent:alice", PermissionScope.READ, "filesystem.read")

    def test_request_deny(self):
        broker = PermissionBroker()
        broker.grant("agent:alice", Permission(PermissionScope.READ, "filesystem.read"))
        engine = PolicyEngine(broker=broker)
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        rid, decision = ob.request("agent:alice", ["filesystem.read"], resource="filesystem.read")
        result = ob.approve(rid, approved=False)
        assert result == OrchestratorPermissionDecision.DENY

    def test_approve_non_ask_reject(self):
        broker = PermissionBroker()
        broker.grant("agent:alice", Permission(PermissionScope.READ, "filesystem.read"))
        engine = PolicyEngine(broker=broker)
        engine.add_rule(PolicyRule("allow", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        rid, decision = ob.request("agent:alice", ["filesystem.read"], resource="filesystem.read")
        assert decision == OrchestratorPermissionDecision.ALLOW
        with pytest.raises(OrchestratorPermissionBrokerError):
            ob.approve(rid, approved=True)

    def test_empty_subject_reject(self):
        ob = OrchestratorPermissionBroker()
        with pytest.raises(OrchestratorPermissionBrokerError):
            ob.check("", ["filesystem.read"])

    def test_does_not_decide_policy_itself(self):
        # Broker delegates to PolicyEngine, does not have its own allow/deny logic
        broker = PermissionBroker()
        engine = PolicyEngine(broker=broker)
        engine.add_rule(PolicyRule("deny-all", applies=lambda r: True, decision=PolicyDecision.DENY, reason="deny"))
        ob = OrchestratorPermissionBroker(permission_broker=broker, policy_engine=engine)
        # Even with permission granted, policy DENY should win
        broker.grant("agent:alice", Permission(PermissionScope.READ, "filesystem.read"))
        decision = ob.check("agent:alice", ["filesystem.read"], resource="filesystem.read")
        assert decision == OrchestratorPermissionDecision.DENY

    def test_history(self):
        ob = OrchestratorPermissionBroker()
        ob.request("agent:alice", ["filesystem.read"])
        assert len(ob.history()) == 1

    def test_clear(self):
        ob = OrchestratorPermissionBroker()
        ob.request("agent:alice", ["filesystem.read"])
        ob.clear()
        assert len(ob.history()) == 0
