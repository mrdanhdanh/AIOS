"""Model health tracker."""

from __future__ import annotations

import time
from typing import Any

from aios.model_router.contracts import ModelHealth


class ModelHealthTracker:
    """Tracks model health and failure counts."""

    def __init__(self) -> None:
        self._health: dict[str, ModelHealth] = {}

    def record_success(self, model_id: str, latency_ms: float = 0.0) -> None:
        if model_id not in self._health:
            self._health[model_id] = ModelHealth(model_id=model_id)
        h = self._health[model_id]
        h.healthy = True
        h.failure_count = 0
        h.avg_latency_ms = latency_ms

    def record_failure(self, model_id: str) -> None:
        if model_id not in self._health:
            self._health[model_id] = ModelHealth(model_id=model_id)
        h = self._health[model_id]
        h.failure_count += 1
        h.last_failure_time = time.time()
        if h.failure_count >= 3:
            h.healthy = False

    def is_healthy(self, model_id: str) -> bool:
        h = self._health.get(model_id)
        return h.healthy if h else True

    def get_health(self, model_id: str) -> ModelHealth:
        if model_id not in self._health:
            self._health[model_id] = ModelHealth(model_id=model_id)
        return self._health[model_id]

    def list_health(self) -> list[ModelHealth]:
        return list(self._health.values())
