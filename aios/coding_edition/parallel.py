"""TASK-209 — Parallel Coding (M26).

Schedule independent coding tasks in parallel, converging Parallel Scheduler
(T028) and Coding Session (T206). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from aios.coding_edition._common import CodingEditionError, _hash


@dataclass
class CodingTask:
    """A unit of parallel coding work (T209)."""

    task_id: str
    depends_on: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.task_id:
            raise CodingEditionError("task_id is required (T001 Rule 1, immutable).")


class ParallelCodingScheduler:
    """Deterministic parallel coding scheduler (T209)."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self._run_id = run_id or f"par-{uuid.uuid4().hex[:12]}"

    @property
    def run_id(self) -> str:
        return self._run_id

    def schedule(self, tasks: List[CodingTask]) -> List[List[str]]:
        """Return deterministic parallel batches (topological, fail-closed).

        Each batch is a set of mutually-independent tasks that can run together.
        """
        ids = {t.task_id for t in tasks}
        for t in tasks:
            for d in t.depends_on:
                if d not in ids:
                    raise CodingEditionError(f"dependency not found: {d}")
        remaining = {t.task_id: set(t.depends_on) for t in tasks}
        batches: List[List[str]] = []
        while remaining:
            ready = sorted(tid for tid, deps in remaining.items() if not deps)
            if not ready:
                raise CodingEditionError("cyclic dependency detected.")
            batches.append(ready)
            done = set(ready)
            remaining = {tid: (deps - done) for tid, deps in remaining.items() if tid not in done}
        return batches

    def scheduler_hash(self, tasks: List[CodingTask]) -> str:
        batches = self.schedule(tasks)
        payload = "||".join(",".join(b) for b in batches)
        return _hash(f"{self._run_id}|{payload}")
