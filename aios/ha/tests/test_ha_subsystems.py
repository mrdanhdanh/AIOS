"""Tests for TASK-041 HA subsystems (health state machine, lease, audit, recovery)."""

from __future__ import annotations

from aios.ha.audit import AuditStore
from aios.ha.contracts import HAConfig
from aios.ha.ha_manager import HAManager
from aios.ha.health import HealthState, HealthStateMachine
from aios.ha.lease import LeaseManager
from aios.ha.recovery import RecoveryManager


def test_health_state_machine_fail_closed() -> None:
    hsm = HealthStateMachine()
    hsm.register("n1")
    assert hsm.is_healthy("n1") is False  # UNKNOWN != HEALTHY
    hsm.set_state("n1", HealthState.HEALTHY)
    assert hsm.is_healthy("n1") is True


def test_lease_single_active() -> None:
    lm = LeaseManager()
    lm.acquire("db", "node-a")
    assert lm.validate("db", "node-a") is True
    try:
        lm.acquire("db", "node-b")
        assert False, "should reject conflicting lease"
    except Exception:
        pass
    lm.release("db", "node-a")
    assert lm.validate("db", "node-a") is False


def test_audit_integrity_chain() -> None:
    store = AuditStore()
    store.append("u", "write", "res-1")
    store.append("u", "delete", "res-2")
    assert store.verify_integrity() is True


def test_recovery_evidence_chain() -> None:
    rm = RecoveryManager()
    rm.record_step("s1", "restart", "ok")
    rm.record_step("s2", "promote", "ok")
    assert rm.verify_chain() is True


def test_ha_manager_wires_subsystems() -> None:
    mgr = HAManager()
    mgr.configure(HAConfig(primary_node="p", replica_nodes=["r1", "r2"]))
    mgr.register_node("r1", healthy=True)
    mgr.register_node("r2", healthy=False)
    new_primary = mgr.failover()
    assert new_primary == "r1"
    assert mgr.audit.verify_integrity() is True
    assert mgr.recovery.verify_chain() is True
