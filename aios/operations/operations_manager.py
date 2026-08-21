"""OperationsManager."""
from __future__ import annotations
import time
from aios.operations.contracts import Operation, OperationLog, OperationStatus

class OperationsManager:
    def __init__(self) -> None:
        self._operations: dict[str, Operation] = {}
        self._logs: dict[str, list[OperationLog]] = {}
    def create_operation(self, op_type: str, target: str = "", details: dict | None = None) -> Operation:
        op = Operation(op_type=op_type, target=target, details=details or {})
        self._operations[op.op_id] = op
        self._logs[op.op_id] = []
        return op
    def execute_operation(self, op_id: str) -> Operation:
        op = self._operations.get(op_id)
        if op is None: raise RuntimeError(f"Operation {op_id!r} not found")
        op.status = OperationStatus.RUNNING
        self._log(op_id, "start", "running")
        op.status = OperationStatus.COMPLETED
        self._log(op_id, "complete", "success")
        return op
    def list_operations(self) -> list[Operation]: return list(self._operations.values())
    def get_operation_logs(self, op_id: str) -> list[OperationLog]: return self._logs.get(op_id, [])
    def _log(self, op_id: str, action: str, result: str) -> None:
        self._logs.setdefault(op_id, []).append(OperationLog(op_id=op_id, action=action, result=result))
