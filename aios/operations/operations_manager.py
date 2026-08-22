"""OperationsManager."""
from __future__ import annotations
import time

from aios.operations.contracts import Operation, OperationLog, OperationStatus
from aios.operations.health import OperationsHealth
from aios.operations.metrics import MetricRecord, OperationsMetrics


class OperationsManager:
    def __init__(self) -> None:
        self._operations: dict[str, Operation] = {}
        self._logs: dict[str, list[OperationLog]] = {}
        self._metrics = OperationsMetrics()
        self._health = OperationsHealth()

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

    def list_operations(self, tenant_id: str = "") -> list[Operation]:
        ops = list(self._operations.values())
        if tenant_id:
            # Server-side tenant isolation: only operations tagged with the tenant.
            ops = [o for o in ops if o.details.get("tenant_id") == tenant_id]
        return ops

    def get_operation_logs(self, op_id: str) -> list[OperationLog]: return self._logs.get(op_id, [])

    def record_metric(self, record: MetricRecord) -> None:
        self._metrics.record(record)

    def metrics_summary(self) -> dict:
        return self._metrics.summarize()

    def set_health(self, name: str, level: str, detail: str = "") -> None:
        from aios.operations.health import OpsHealthLevel
        self._health.set(name, OpsHealthLevel(level), detail)

    def health(self) -> dict:
        return self._health.to_dict()

    def is_healthy(self) -> bool:
        return self._health.is_healthy()

    def overview(self) -> dict:
        return {
            "operation_count": len(self._operations),
            "health": self._health.to_dict(),
            "metrics": self._metrics.summarize(),
        }

    def _log(self, op_id: str, action: str, result: str) -> None:
        self._logs.setdefault(op_id, []).append(OperationLog(op_id=op_id, action=action, result=result))
