"""Data models for the Task Registry (Rule 1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    """Lifecycle / governance status of a task.

    The ordered lifecycle states (PLANNED -> ... -> DONE) are enforced by
    :mod:`aios.governance.lifecycle`. ``DEPRECATED`` and ``BLOCKED`` are
    terminal governance statuses managed by the registry / gates.
    """

    PLANNED = "PLANNED"
    SPECIFIED = "SPECIFIED"
    CRITIQUED_1 = "CRITIQUED_1"
    CRITIQUED_2 = "CRITIQUED_2"
    BROKEN_DOWN = "BROKEN_DOWN"
    REVIEWED = "REVIEWED"
    IMPLEMENTING = "IMPLEMENTING"
    TESTING = "TESTING"
    EVALUATING = "EVALUATING"
    REGRESSION = "REGRESSION"
    READY_TO_CLOSE = "READY_TO_CLOSE"
    DONE = "DONE"
    DEPRECATED = "DEPRECATED"
    BLOCKED = "BLOCKED"

    def is_terminal(self) -> bool:
        return self in (TaskStatus.DONE, TaskStatus.DEPRECATED)


@dataclass
class Task:
    """A registered task.

    ``task_id`` is immutable once created. ``dependencies`` is the direct
    dependency set used by the dependency graph (Rule 2).
    """

    task_id: str
    title: str
    milestone: str = ""
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PLANNED
    created_at: str = ""

    def __post_init__(self) -> None:
        # Guard against accidental reuse of a deprecated id at the data layer.
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
