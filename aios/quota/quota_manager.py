"""QuotaManager."""
from __future__ import annotations
from aios.quota.contracts import Quota, QuotaUsage

class QuotaManager:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str], Quota] = {}
    def set_quota(self, tenant_id: str, resource_type: str, limit: int) -> Quota:
        q = Quota(tenant_id=tenant_id, resource_type=resource_type, limit=limit)
        self._quotas[(tenant_id, resource_type)] = q
        return q
    def check_quota(self, tenant_id: str, resource_type: str) -> Quota | None:
        return self._quotas.get((tenant_id, resource_type))
    def consume_quota(self, tenant_id: str, resource_type: str, amount: int = 1) -> bool:
        q = self._quotas.get((tenant_id, resource_type))
        if q is None: return False
        if q.exceeded: return False
        q.used += amount
        return True
    def get_usage(self, tenant_id: str, resource_type: str) -> QuotaUsage | None:
        q = self._quotas.get((tenant_id, resource_type))
        if q is None: return None
        return QuotaUsage(tenant_id=q.tenant_id, resource_type=q.resource_type, used=q.used, limit=q.limit)
    def reset_quota(self, tenant_id: str, resource_type: str) -> None:
        q = self._quotas.get((tenant_id, resource_type))
        if q: q.used = 0
