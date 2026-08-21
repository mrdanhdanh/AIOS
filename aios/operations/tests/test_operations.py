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
