"""Tests for the resource/network/command policy (T138)."""

import pytest

from aios.execution import Decision, ExecutionPolicy, PolicyEngine, ResourceLimit
from aios.execution._common import ExecutionError


def test_resource_limit_positive():
    with pytest.raises(ExecutionError):
        ResourceLimit(cpu=0, mem_mb=10)
    with pytest.raises(ExecutionError):
        ResourceLimit(cpu=1, mem_mb=0)


def test_policy_requires_execution_ref():
    with pytest.raises(ExecutionError):
        ExecutionPolicy(execution_ref="", resource_limit=ResourceLimit(1, 100), network_egress=True)


def test_register_duplicate_id():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(1, 100), network_egress=True, policy_id="pol1")
    e.register(p)
    with pytest.raises(ExecutionError):
        e.register(p)


def test_evaluate_allow():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(2, 200), network_egress=True, policy_id="pol1")
    e.register(p)
    d = e.evaluate("pol1", "pytest")
    assert d.decision == Decision.ALLOW


def test_evaluate_deny_cpu():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(1, 200), network_egress=True, policy_id="pol1")
    e.register(p)
    d = e.evaluate("pol1", "pytest", cpu_request=2)
    assert d.decision == Decision.DENY


def test_evaluate_deny_mem():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(2, 100), network_egress=True, policy_id="pol1")
    e.register(p)
    d = e.evaluate("pol1", "pytest", mem_request=200)
    assert d.decision == Decision.DENY


def test_evaluate_deny_network():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(2, 200), network_egress=False, policy_id="pol1")
    e.register(p)
    d = e.evaluate("pol1", "pytest", network_egress=True)
    assert d.decision == Decision.DENY


def test_evaluate_deny_command():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(2, 200), network_egress=True, command_allowlist=("pytest",), policy_id="pol1")
    e.register(p)
    d = e.evaluate("pol1", "rm")
    assert d.decision == Decision.DENY


def test_provenance():
    e = PolicyEngine()
    p = ExecutionPolicy(execution_ref="ex1", resource_limit=ResourceLimit(2, 200), network_egress=True, policy_id="pol1")
    e.register(p)
    prov = e.provenance("pol1")
    assert prov["policy_id"] == "pol1"
    assert prov["content_hash"]
