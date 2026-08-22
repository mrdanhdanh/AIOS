"""Operations metrics — aggregated by tenant / project / user dimensions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricRecord:
    name: str
    value: float
    tenant_id: str = ""
    project_id: str = ""
    user_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
        }


class OperationsMetrics:
    """Collects and aggregates operations metrics by dimension."""

    def __init__(self) -> None:
        self._records: list[MetricRecord] = []

    def record(self, record: MetricRecord) -> None:
        self._records.append(record)

    def by_tenant(self, tenant_id: str) -> list[MetricRecord]:
        return [r for r in self._records if r.tenant_id == tenant_id]

    def summarize(self) -> dict[str, Any]:
        tenants: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        projects: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        users: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for r in self._records:
            tenants[r.tenant_id][r.name] = tenants[r.tenant_id].get(r.name, 0.0) + r.value
            projects[r.project_id][r.name] = projects[r.project_id].get(r.name, 0.0) + r.value
            users[r.user_id][r.name] = users[r.user_id].get(r.name, 0.0) + r.value
        return {
            "by_tenant": {k: dict(v) for k, v in tenants.items()},
            "by_project": {k: dict(v) for k, v in projects.items()},
            "by_user": {k: dict(v) for k, v in users.items()},
        }
