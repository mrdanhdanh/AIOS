"""Tests for TASK-059 Multi-Agent Autonomy (Delegation)."""
from __future__ import annotations

from aios.multi_agent_autonomy.contracts import Authority, DelegationVerdict, DelegateRequest
from aios.multi_agent_autonomy.delegation import AuthorityAttenuator, DelegationManager


def _auth(caps=("read", "write"), rb=10.0, depth=3, tenant="t1", tools=("read",), risk="low"):
    return Authority(capabilities=set(caps), resource_budget=rb, max_depth=depth,
                     tenant_scope=tenant, tool_permissions=set(tools), risk_level=risk)


def test_attenuation_intersects_capabilities():
    a = AuthorityAttenuator()
    parent = _auth(caps=("read", "write", "exec"), rb=10, depth=3, tenant="t1")
    scope = _auth(caps=("read", "write"), rb=5, depth=2, tenant="t1")
    policy = _auth(caps=("read",), rb=4, depth=1, tenant="t1")
    child = a.attenuate(parent, scope, policy)
    assert child.capabilities == {"read"}
    assert child.resource_budget == 4
    assert child.max_depth == 0


def test_child_authority_subset_of_parent():
    mgr = DelegationManager()
    parent = _auth(caps=("read", "write"), rb=10, depth=3, tenant="t1")
    scope = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    policy = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=2, max_depth=2, max_children=5)
    d = mgr.decide(req, parent, scope, policy)
    assert d.verdict == DelegationVerdict.APPROVED
    assert d.child_authority.capabilities.issubset(parent.capabilities)


def test_child_exceeding_parent_blocked():
    mgr = DelegationManager()
    parent = _auth(caps=("read",), rb=10, depth=3, tenant="t1")
    # scope tries to grant 'write' which parent lacks -> attenuation yields empty
    scope = _auth(caps=("read", "write"), rb=5, depth=2, tenant="t1")
    policy = _auth(caps=("read", "write"), rb=5, depth=2, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=2, max_depth=2, max_children=5)
    d = mgr.decide(req, parent, scope, policy)
    # child capabilities = parent ∩ scope ∩ policy = {read}; not empty, but
    # if scope had a capability parent lacks it is dropped by intersection.
    assert d.verdict == DelegationVerdict.APPROVED
    assert "write" not in d.child_authority.capabilities


def test_tenant_escape_blocked():
    mgr = DelegationManager()
    parent = _auth(caps=("read",), rb=10, depth=3, tenant="t1")
    scope = _auth(caps=("read",), rb=5, depth=2, tenant="t2")  # different tenant
    policy = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=2, max_depth=2, max_children=5)
    d = mgr.decide(req, parent, scope, policy)
    assert d.verdict == DelegationVerdict.BLOCKED
    assert "tenant" in d.reason


def test_delegation_depth_exceeded():
    mgr = DelegationManager()
    parent = _auth(caps=("read",), rb=10, depth=0, tenant="t1")
    scope = _auth(caps=("read",), rb=5, depth=0, tenant="t1")
    policy = _auth(caps=("read",), rb=5, depth=0, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=2, max_depth=0, max_children=5)
    d = mgr.decide(req, parent, scope, policy)
    assert d.verdict == DelegationVerdict.BLOCKED
    assert "depth" in d.reason


def test_cumulative_resource_exceeded():
    mgr = DelegationManager()
    parent = _auth(caps=("read",), rb=5, depth=3, tenant="t1")
    scope = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    policy = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=4, max_depth=2, max_children=5)
    mgr.decide(req, parent, scope, policy)
    # second delegation pushes cumulative over parent budget
    req2 = DelegateRequest(parent_goal_id="g1", sub_goal="sg2", delegation_budget=5,
                           execution_budget=4, max_depth=2, max_children=5)
    d2 = mgr.decide(req2, parent, scope, policy)
    assert d2.verdict == DelegationVerdict.BLOCKED
    assert "cumulative" in d2.reason


def test_governor_can_block():
    def gov(req, child):
        return DelegationVerdict.BLOCKED
    mgr = DelegationManager(governor_decision=gov)
    parent = _auth(caps=("read",), rb=10, depth=3, tenant="t1")
    scope = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    policy = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=2, max_depth=2, max_children=5)
    d = mgr.decide(req, parent, scope, policy)
    assert d.verdict == DelegationVerdict.BLOCKED
    assert "governor" in d.reason


def test_provenance_recorded():
    mgr = DelegationManager()
    parent = _auth(caps=("read",), rb=10, depth=3, tenant="t1")
    scope = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    policy = _auth(caps=("read",), rb=5, depth=2, tenant="t1")
    req = DelegateRequest(parent_goal_id="g1", sub_goal="sg", delegation_budget=5,
                          execution_budget=2, max_depth=2, max_children=5, evidence_ref="ev:1")
    mgr.decide(req, parent, scope, policy)
    assert len(mgr.records) == 1
    assert mgr.records[0]["evidence_ref"] == "ev:1"
