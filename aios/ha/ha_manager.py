"""HAManager."""
from __future__ import annotations

from aios.ha.audit import AuditStore
from aios.ha.contracts import HAConfig, RecoveryPlan
from aios.ha.health import HealthState, HealthStateMachine
from aios.ha.lease import LeaseManager
from aios.ha.recovery import RecoveryManager


class HAManager:
    def __init__(self) -> None:
        self._config = HAConfig()
        self._node_health: dict[str, bool] = {}
        self._recovery_plans: dict[str, RecoveryPlan] = {}
        self._health = HealthStateMachine()
        self._leases = LeaseManager()
        self._recovery = RecoveryManager()
        self._audit = AuditStore()

    def configure(self, config: HAConfig) -> None: self._config = config

    def register_node(self, node_id: str, healthy: bool = True) -> None:
        self._node_health[node_id] = healthy
        self._health.set_state(
            node_id,
            HealthState.HEALTHY if healthy else HealthState.UNHEALTHY,
        )

    def health_check(self, node_id: str) -> bool: return self._node_health.get(node_id, False)

    def failover(self) -> str | None:
        if not self._config.primary_node: return None
        # Respect single-active lease: release old primary, acquire on replica.
        self._leases.release(self._config.primary_node, self._config.primary_node)
        for r in self._config.replica_nodes:
            if self._node_health.get(r, False):
                self._leases.acquire(self._config.primary_node, r)
                self._config.primary_node = r
                self._audit.append("ha_manager", "failover", r)
                return r
        return None

    def get_status(self) -> dict:
        return {
            "primary": self._config.primary_node,
            "replicas": self._config.replica_nodes,
            "health": dict(self._node_health),
            "health_states": self._health.status(),
        }

    def create_recovery_plan(self, steps: list) -> RecoveryPlan:
        plan = RecoveryPlan(steps=steps)
        self._recovery_plans[plan.plan_id] = plan
        # Record an evidence chain for the recovery steps.
        for i, step in enumerate(steps):
            self._recovery.record_step(f"step-{i}", str(step), "planned")
        self._audit.append("ha_manager", "create_recovery_plan", plan.plan_id)
        return plan

    # --- Surfaces for the new HA subsystems ---
    @property
    def health(self) -> HealthStateMachine:
        return self._health

    @property
    def leases(self) -> LeaseManager:
        return self._leases

    @property
    def recovery(self) -> RecoveryManager:
        return self._recovery

    @property
    def audit(self) -> AuditStore:
        return self._audit
