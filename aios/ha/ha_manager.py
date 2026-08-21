"""HAManager."""
from __future__ import annotations
from aios.ha.contracts import HAConfig, RecoveryPlan

class HAManager:
    def __init__(self) -> None:
        self._config = HAConfig()
        self._node_health: dict[str, bool] = {}
        self._recovery_plans: dict[str, RecoveryPlan] = {}
    def configure(self, config: HAConfig) -> None: self._config = config
    def register_node(self, node_id: str, healthy: bool = True) -> None: self._node_health[node_id] = healthy
    def health_check(self, node_id: str) -> bool: return self._node_health.get(node_id, False)
    def failover(self) -> str | None:
        if not self._config.primary_node: return None
        for r in self._config.replica_nodes:
            if self._node_health.get(r, False):
                self._config.primary_node = r
                return r
        return None
    def get_status(self) -> dict: return {"primary": self._config.primary_node, "replicas": self._config.replica_nodes, "health": dict(self._node_health)}
    def create_recovery_plan(self, steps: list) -> RecoveryPlan:
        plan = RecoveryPlan(steps=steps)
        self._recovery_plans[plan.plan_id] = plan
        return plan
