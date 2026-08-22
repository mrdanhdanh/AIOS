"""Idempotency guard (TASK-066).

Ensures a step already executed (done) is never re-executed with double
side-effects. Tracks executed ``step_id``s and short-circuits re-execution,
which is what makes a resume from a verified checkpoint safe: a step that was
already completed before the crash is not run again on recovery.

Layering: ``durable`` is a runtime-level durability concern; it imports no
peer packages directly.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class StepOutcome:
    """Result of a guarded step execution."""

    executed: bool
    result: Any = None


class IdempotencyGuard:
    """Tracks executed step_ids and prevents double side-effects on resume."""

    def __init__(self) -> None:
        self._done: set[str] = set()
        self._results: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def is_done(self, step_id: str) -> bool:
        with self._lock:
            return step_id in self._done

    def mark_done(self, step_id: str, result: Any = None) -> None:
        with self._lock:
            self._done.add(step_id)
            if result is not None:
                self._results[step_id] = result

    def execute_once(self, step_id: str, action: Callable[[], Any]) -> StepOutcome:
        """Run ``action`` at most once per ``step_id``.

        If the step was already executed, the action is NOT run again (no
        double side-effect) and the previously captured result is returned.
        """
        with self._lock:
            if step_id in self._done:
                return StepOutcome(executed=False, result=self._results.get(step_id))
        result = action()
        with self._lock:
            self._done.add(step_id)
            self._results[step_id] = result
        return StepOutcome(executed=True, result=result)
