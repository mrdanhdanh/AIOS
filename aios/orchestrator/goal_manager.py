"""Goal Manager — lifecycle + persistence for long-running goals (TASK-012).

Manages goals that span multiple tasks and sessions. State is persistent
(to_dict/from_dict + file) so a goal can resume after process restart.

Layering: orchestrator — may import runtime/capability/tool/unknown.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["GoalStatus", "Goal", "GoalManager", "GoalError"]


class GoalError(Exception):
    pass


class GoalStatus(str, Enum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Valid transitions per spec §3.3
_VALID_TRANSITIONS: Dict[GoalStatus, set] = {
    GoalStatus.CREATED: {GoalStatus.PLANNED, GoalStatus.CANCELLED},
    GoalStatus.PLANNED: {GoalStatus.ACTIVE, GoalStatus.CANCELLED},
    GoalStatus.ACTIVE: {GoalStatus.PAUSED, GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.CANCELLED},
    GoalStatus.PAUSED: {GoalStatus.ACTIVE, GoalStatus.CANCELLED, GoalStatus.FAILED},
    GoalStatus.COMPLETED: set(),
    GoalStatus.FAILED: set(),
    GoalStatus.CANCELLED: set(),
}

_ALLOWED_PRIORITIES = {"critical", "high", "normal", "low"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Goal:
    """Goal contract per T012 §3.2."""

    id: str
    title: str
    description: str = ""
    status: GoalStatus = GoalStatus.CREATED
    tasks: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    # Execution references for evidence
    execution_refs: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = GoalStatus(self.status)
            except ValueError as exc:
                raise GoalError(f"invalid status {self.status!r}") from exc

    def validate(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise GoalError("goal id must be non-empty string")
        if not isinstance(self.title, str) or not self.title.strip():
            raise GoalError("goal title must be non-empty string")
        if self.priority not in _ALLOWED_PRIORITIES:
            raise GoalError(f"priority {self.priority!r} not in {sorted(_ALLOWED_PRIORITIES)}")
        if not isinstance(self.tasks, list):
            raise GoalError("tasks must be a list")
        for t in self.tasks:
            if not isinstance(t, str) or not t.strip():
                raise GoalError(f"task id {t!r} must be non-empty string")

    def touch(self) -> None:
        self.updated_at = _now()

    def transition(self, target: GoalStatus) -> None:
        if isinstance(target, str):
            target = GoalStatus(target)
        if target == self.status:
            return
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if target not in allowed:
            raise GoalError(f"invalid transition {self.status.value} -> {target.value}")
        self.status = target
        self.touch()

    def progress(self, task_statuses: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Compute progress. If task_statuses provided, use it; else use tasks count."""
        total = len(self.tasks)
        if total == 0:
            return {"completed": 0, "total": 0, "percent": 0.0, "status": self.status.value}
        if task_statuses is None:
            # Without external statuses, progress is 0 until COMPLETED
            completed = 1 if self.status == GoalStatus.COMPLETED else 0
            # But if tasks list exists, we can't know; return 0
            if self.status == GoalStatus.COMPLETED:
                completed = total
            else:
                completed = 0
            return {"completed": completed, "total": total, "percent": (completed / total * 100) if total else 0.0, "status": self.status.value}
        completed = sum(1 for tid in self.tasks if task_statuses.get(tid) == "SUCCEEDED")
        failed = sum(1 for tid in self.tasks if task_statuses.get(tid) == "FAILED")
        blocked = sum(1 for tid in self.tasks if task_statuses.get(tid) == "BLOCKED")
        percent = (completed / total * 100) if total else 0.0
        return {
            "completed": completed,
            "total": total,
            "percent": percent,
            "failed": failed,
            "blocked": blocked,
            "status": self.status.value,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value if isinstance(self.status, GoalStatus) else str(self.status),
            "tasks": list(self.tasks),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
            "priority": self.priority,
            "execution_refs": dict(self.execution_refs),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        if not isinstance(data, dict):
            raise GoalError("goal data must be a mapping")
        gid = data.get("id")
        title = data.get("title")
        if not gid or not isinstance(gid, str) or not gid.strip():
            raise GoalError("goal id must be non-empty string")
        if not title or not isinstance(title, str) or not title.strip():
            raise GoalError("goal title must be non-empty string")
        status_raw = data.get("status", GoalStatus.CREATED.value)
        try:
            status = GoalStatus(status_raw)
        except ValueError as exc:
            raise GoalError(f"invalid status {status_raw!r}") from exc
        obj = cls(
            id=str(gid),
            title=str(title),
            description=str(data.get("description", "") or ""),
            status=status,
            tasks=list(data.get("tasks", []) or []),
            created_at=str(data.get("created_at", _now())),
            updated_at=str(data.get("updated_at", _now())),
            metadata=dict(data.get("metadata", {}) or {}),
            priority=str(data.get("priority", "normal") or "normal"),
            execution_refs=dict(data.get("execution_refs", {}) or {}),
        )
        obj.validate()
        return obj


class GoalManager:
    """Thread-safe manager for goals with persistence."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._goals: Dict[str, Goal] = {}

    def create_goal(
        self,
        title: str,
        description: str = "",
        goal_id: Optional[str] = None,
        tasks: Optional[List[str]] = None,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Goal:
        gid = goal_id or f"goal-{uuid.uuid4().hex[:12]}"
        goal = Goal(
            id=gid,
            title=title,
            description=description,
            status=GoalStatus.CREATED,
            tasks=list(tasks or []),
            metadata=dict(metadata or {}),
            priority=priority,
        )
        goal.validate()
        with self._lock:
            if gid in self._goals:
                raise GoalError(f"goal {gid!r} already exists")
            self._goals[gid] = goal
        return goal

    def get(self, goal_id: str) -> Goal:
        with self._lock:
            g = self._goals.get(goal_id)
            if g is None:
                raise GoalError(f"unknown goal {goal_id!r}")
            return g

    def list(self) -> List[Goal]:
        with self._lock:
            return sorted(self._goals.values(), key=lambda g: g.created_at)

    def update(self, goal: Goal) -> None:
        goal.validate()
        with self._lock:
            if goal.id not in self._goals:
                raise GoalError(f"unknown goal {goal.id!r}")
            self._goals[goal.id] = goal

    def transition(self, goal_id: str, target: GoalStatus) -> Goal:
        with self._lock:
            g = self.get(goal_id)
            g.transition(target)
            return g

    def pause(self, goal_id: str) -> Goal:
        return self.transition(goal_id, GoalStatus.PAUSED)

    def resume(self, goal_id: str) -> Goal:
        return self.transition(goal_id, GoalStatus.ACTIVE)

    def cancel(self, goal_id: str) -> Goal:
        return self.transition(goal_id, GoalStatus.CANCELLED)

    def add_task(self, goal_id: str, task_id: str) -> Goal:
        with self._lock:
            g = self.get(goal_id)
            if task_id in g.tasks:
                raise GoalError(f"task {task_id!r} already in goal {goal_id!r}")
            g.tasks.append(task_id)
            g.touch()
            return g

    def remove_task(self, goal_id: str, task_id: str) -> Goal:
        with self._lock:
            g = self.get(goal_id)
            if task_id not in g.tasks:
                raise GoalError(f"task {task_id!r} not in goal {goal_id!r}")
            g.tasks.remove(task_id)
            g.touch()
            return g

    def progress(self, goal_id: str, task_statuses: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        with self._lock:
            g = self.get(goal_id)
            return g.progress(task_statuses)

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {gid: g.to_dict() for gid, g in self._goals.items()}

    def save_to_file(self, path: str) -> None:
        data = self.to_dict()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def load_from_file(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            raise GoalError(f"file not found: {path}")
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise GoalError("goal file must contain a mapping")
        with self._lock:
            self._goals.clear()
            for gid, gdata in data.items():
                g = Goal.from_dict(gdata)
                self._goals[gid] = g

    def clear(self) -> None:
        with self._lock:
            self._goals.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._goals)

    def __contains__(self, goal_id: str) -> bool:
        with self._lock:
            return goal_id in self._goals
