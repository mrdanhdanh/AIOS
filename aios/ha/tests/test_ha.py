"""Tests for HA module."""
from __future__ import annotations
import pytest
from aios.ha.contracts import HAConfig, RecoveryPlan
from aios.ha.ha_manager import HAManager

class TestHA:
    def test_configure(self):
        mgr = HAManager()
        mgr.configure(HAConfig(primary_node="n1", replica_nodes=["n2", "n3"]))
        assert mgr.get_status()["primary"] == "n1"
    def test_health_check(self):
        mgr = HAManager()
        mgr.register_node("n1", True)
        assert mgr.health_check("n1")
        assert not mgr.health_check("n2")
    def test_failover(self):
        mgr = HAManager()
        mgr.configure(HAConfig(primary_node="n1", replica_nodes=["n2"]))
        mgr.register_node("n1", False)
        mgr.register_node("n2", True)
        result = mgr.failover()
        assert result == "n2"
        assert mgr.get_status()["primary"] == "n2"
    def test_failover_no_replica(self):
        mgr = HAManager()
        mgr.configure(HAConfig(primary_node="n1"))
        result = mgr.failover()
        assert result is None
    def test_recovery_plan(self):
        mgr = HAManager()
        plan = mgr.create_recovery_plan(["step1", "step2"])
        assert len(plan.steps) == 2
