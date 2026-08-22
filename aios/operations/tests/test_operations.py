"""Tests for operations module."""
from __future__ import annotations
import pytest
from aios.operations.contracts import Operation, OperationLog, OperationStatus
from aios.operations.operations_manager import OperationsManager

class TestOperations:
    def test_create_operation(self):
        mgr = OperationsManager()
        op = mgr.create_operation("deploy", target="prod")
        assert op.op_type == "deploy"
        assert op.status == OperationStatus.PENDING
    def test_execute(self):
        mgr = OperationsManager()
        op = mgr.create_operation("backup")
        result = mgr.execute_operation(op.op_id)
        assert result.status == OperationStatus.COMPLETED
    def test_logs(self):
        mgr = OperationsManager()
        op = mgr.create_operation("test")
        mgr.execute_operation(op.op_id)
        logs = mgr.get_operation_logs(op.op_id)
        assert len(logs) >= 2
    def test_list_operations(self):
        mgr = OperationsManager()
        mgr.create_operation("a"); mgr.create_operation("b")
        assert len(mgr.list_operations()) == 2
    def test_not_found(self):
        mgr = OperationsManager()
        with pytest.raises(RuntimeError): mgr.execute_operation("nonexistent")


class TestOperationsT042:
    def test_health_fail_closed(self):
        from aios.operations.health import OpsHealthLevel, OperationsHealth
        h = OperationsHealth()
        assert h.is_healthy() is False  # UNKNOWN
        h.set("api", OpsHealthLevel.HEALTHY)
        assert h.is_healthy() is True

    def test_metrics_dimensions(self):
        from aios.operations.metrics import MetricRecord, OperationsMetrics
        m = OperationsMetrics()
        m.record(MetricRecord("requests", 5, tenant_id="t1", project_id="p1", user_id="u1"))
        m.record(MetricRecord("requests", 3, tenant_id="t1"))
        summary = m.summarize()
        assert summary["by_tenant"]["t1"]["requests"] == 8
        assert summary["by_user"]["u1"]["requests"] == 5

    def test_operations_tenant_isolation(self):
        mgr = OperationsManager()
        op1 = mgr.create_operation("backup", details={"tenant_id": "t1"})
        mgr.create_operation("backup", details={"tenant_id": "t2"})
        assert len(mgr.list_operations("t1")) == 1
        assert mgr.list_operations("t1")[0].op_id == op1.op_id

    def test_operations_overview_and_health(self):
        mgr = OperationsManager()
        mgr.create_operation("deploy")
        mgr.set_health("runtime", "healthy")
        ov = mgr.overview()
        assert ov["operation_count"] == 1
        assert ov["health"]["overall"] == "healthy"
        assert mgr.is_healthy() is True
