"""Task Queue — logical queue for Orchestrator (TASK-012).

Logical queue: "which task should be processed next?" — not technical
scheduling (Scheduler Service handles "when"). Dependency-aware, priority-aware
but priority never overrides dependency. Persistent, thread-safe, fail-closed.

Layering: orchestrator — may import runtime/capability/tool/unknown.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["TaskStatus", "TaskPriority", "Task", "TaskQueue", "TaskQueueError"]


class TaskQueueError(Exception):
    pass


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    BLOCKED = "BLOCKED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


_PRIORITY_ORDER: Dict[TaskPriority, int] = {
    TaskPriority.CRITICAL: 0,
    TaskPriority.HIGH: 1,
    TaskPriority.NORMAL: 2,
    TaskPriority.LOW: 3,
}

_VALID_TRANSITIONS: Dict[TaskStatus, set] = {
    TaskStatus.PENDING: {TaskStatus.READY, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.READY: {TaskStatus.RUNNING, TaskStatus.PAUSED, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.PAUSED, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.PAUSED: {TaskStatus.READY, TaskStatus.PENDING, TaskStatus.CANCELLED, TaskStatus.BLOCKED},
    TaskStatus.BLOCKED: {TaskStatus.READY, TaskStatus.PENDING, TaskStatus.CANCELLED},
    TaskStatus.SUCCEEDED: set(),
    TaskStatus.FAILED: {TaskStatus.READY, TaskStatus.PENDING, TaskStatus.CANCELLED},  # retry
    TaskStatus.CANCELLED: set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Task:
    """Task contract per T012 §5."""

    id: str
    goal_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    attempts: int = 0
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = TaskStatus(self.status)
            except ValueError as exc:
                raise TaskQueueError(f"invalid status {self.status!r}") from exc
        if isinstance(self.priority, str):
            try:
                self.priority = TaskPriority(self.priority)
            except ValueError as exc:
                raise TaskQueueError(f"invalid priority {self.priority!r}") from exc

    def validate(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise TaskQueueError("task id must be non-empty string")
        if self.goal_id is not None and (not isinstance(self.goal_id, str) or not self.goal_id.strip()):
            raise TaskQueueError("goal_id must be non-empty string if provided")
        if not isinstance(self.dependencies, list):
            raise TaskQueueError("dependencies must be a list")
        for d in self.dependencies:
            if not isinstance(d, str) or not d.strip():
                raise TaskQueueError(f"dependency {d!r} must be non-empty string")
            if d == self.id:
                raise TaskQueueError(f"task {self.id!r} cannot depend on itself")
        if not isinstance(self.attempts, int) or self.attempts < 0:
            raise TaskQueueError("attempts must be >= 0")

    def touch(self) -> None:
        self.updated_at = _now()

    def transition(self, target: TaskStatus) -> None:
        if isinstance(target, str):
            target = TaskStatus(target)
        if target == self.status:
            return
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if target not in allowed:
            raise TaskQueueError(f"invalid transition {self.status.value} -> {target.value} for task {self.id!r}")
        self.status = target
        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "status": self.status.value if isinstance(self.status, TaskStatus) else str(self.status),
            "priority": self.priority.value if isinstance(self.priority, TaskPriority) else str(self.priority),
            "dependencies": list(self.dependencies),
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "attempts": self.attempts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        if not isinstance(data, dict):
            raise TaskQueueError("task data must be a mapping")
        tid = data.get("id")
        if not tid or not isinstance(tid, str) or not tid.strip():
            raise TaskQueueError("task id must be non-empty string")
        status_raw = data.get("status", TaskStatus.PENDING.value)
        try:
            status = TaskStatus(status_raw)
        except ValueError as exc:
            raise TaskQueueError(f"invalid status {status_raw!r}") from exc
        priority_raw = data.get("priority", TaskPriority.NORMAL.value)
        try:
            priority = TaskPriority(priority_raw)
        except ValueError as exc:
            raise TaskQueueError(f"invalid priority {priority_raw!r}") from exc
        obj = cls(
            id=str(tid),
            goal_id=data.get("goal_id"),
            status=status,
            priority=priority,
            dependencies=list(data.get("dependencies", []) or []),
            workflow_id=data.get("workflow_id"),
            execution_id=data.get("execution_id"),
            attempts=int(data.get("attempts", 0)),
            created_at=str(data.get("created_at", _now())),
            updated_at=str(data.get("updated_at", _now())),
            metadata=dict(data.get("metadata", {}) or {}),
        )
        obj.validate()
        return obj


class TaskQueue:
    """Logical task queue — dependency and priority aware, persistent."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tasks: Dict[str, Task] = {}
        self._order: List[str] = []  # insertion order for stable dequeue

    # -- CRUD -------------------------------------------------------------
    def enqueue(self, task: Task) -> Task:
        task.validate()
        with self._lock:
            if task.id in self._tasks:
                raise TaskQueueError(f"task {task.id!r} already enqueued")
            # Validate dependencies exist or allow forward refs? Require existence check is optional;
            # we allow dependencies that are not yet enqueued but will be BLOCKED until they appear and succeed.
            self._tasks[task.id] = task
            self._order.append(task.id)
            # Auto-evaluate READY vs BLOCKED vs PENDING
            self._evaluate_status(task.id)
            return task

    def create_task(
        self,
        task_id: Optional[str] = None,
        goal_id: Optional[str] = None,
        priority: str = "NORMAL",
        dependencies: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        tid = task_id or f"task-{uuid.uuid4().hex[:12]}"
        try:
            prio = TaskPriority(priority)
        except ValueError as exc:
            raise TaskQueueError(f"invalid priority {priority!r}") from exc
        task = Task(
            id=tid,
            goal_id=goal_id,
            status=TaskStatus.PENDING,
            priority=prio,
            dependencies=list(dependencies or []),
            workflow_id=workflow_id,
            metadata=dict(metadata or {}),
        )
        return self.enqueue(task)

    def get(self, task_id: str) -> Task:
        with self._lock:
            t = self._tasks.get(task_id)
            if t is None:
                raise TaskQueueError(f"unknown task {task_id!r}")
            return t

    def list(self) -> List[Task]:
        with self._lock:
            return [self._tasks[tid] for tid in self._order if tid in self._tasks]

    def list_by_status(self, status: TaskStatus) -> List[Task]:
        if isinstance(status, str):
            status = TaskStatus(status)
        with self._lock:
            return [t for t in self._tasks.values() if t.status == status]

    def list_by_goal(self, goal_id: str) -> List[Task]:
        with self._lock:
            return [t for t in self._tasks.values() if t.goal_id == goal_id]

    # -- Status evaluation ------------------------------------------------
    def _is_dependency_satisfied(self, task: Task) -> bool:
        for dep_id in task.dependencies:
            dep = self._tasks.get(dep_id)
            if dep is None:
                return False
            if dep.status != TaskStatus.SUCCEEDED:
                return False
        return True

    def _evaluate_status(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if task is None:
            return
        if task.status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.RUNNING, TaskStatus.PAUSED):
            return
        if task.dependencies:
            if not self._is_dependency_satisfied(task):
                if task.status != TaskStatus.BLOCKED:
                    task.status = TaskStatus.BLOCKED
                    task.touch()
                return
            else:
                if task.status == TaskStatus.BLOCKED:
                    task.status = TaskStatus.READY
                    task.touch()
                    return
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.READY
                    task.touch()
                    return
        else:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.READY
                task.touch()
            # BLOCKED with no dependencies stays BLOCKED until explicit unblock()

    def evaluate_all(self) -> None:
        with self._lock:
            for tid in list(self._tasks.keys()):
                self._evaluate_status(tid)

    # -- Queue operations -------------------------------------------------
    def peek(self) -> Optional[Task]:
        with self._lock:
            self.evaluate_all()
            candidates = [t for t in self._tasks.values() if t.status == TaskStatus.READY]
            if not candidates:
                return None
            # Sort by priority then insertion order
            candidates.sort(key=lambda t: (_PRIORITY_ORDER[t.priority], self._order.index(t.id) if t.id in self._order else 9999))
            return candidates[0]

    def dequeue(self) -> Optional[Task]:
        with self._lock:
            task = self.peek()
            if task is None:
                return None
            task.transition(TaskStatus.RUNNING)
            return task

    def pause(self, task_id: str) -> Task:
        with self._lock:
            t = self.get(task_id)
            t.transition(TaskStatus.PAUSED)
            return t

    def resume(self, task_id: str) -> Task:
        with self._lock:
            t = self.get(task_id)
            if t.status != TaskStatus.PAUSED:
                raise TaskQueueError(f"task {task_id!r} is not PAUSED (is {t.status.value})")
            # Resume to READY if dependencies satisfied else BLOCKED/PENDING
            if t.dependencies and not self._is_dependency_satisfied(t):
                t.status = TaskStatus.BLOCKED
            else:
                t.status = TaskStatus.READY
            t.touch()
            return t

    def cancel(self, task_id: str) -> Task:
        with self._lock:
            t = self.get(task_id)
            t.transition(TaskStatus.CANCELLED)
            return t

    def block(self, task_id: str) -> Task:
        with self._lock:
            t = self.get(task_id)
            if t.status in (TaskStatus.SUCCEEDED, TaskStatus.CANCELLED):
                raise TaskQueueError(f"cannot block task in {t.status.value}")
            t.status = TaskStatus.BLOCKED
            t.touch()
            return t

    def unblock(self, task_id: str) -> Task:
        with self._lock:
            t = self.get(task_id)
            if t.status != TaskStatus.BLOCKED:
                raise TaskQueueError(f"task {task_id!r} is not BLOCKED")
            if t.dependencies and not self._is_dependency_satisfied(t):
                # Still blocked by dependency
                return t
            t.status = TaskStatus.READY
            t.touch()
            return t

    def complete(self, task_id: str, success: bool = True) -> Task:
        with self._lock:
            t = self.get(task_id)
            if t.status != TaskStatus.RUNNING:
                raise TaskQueueError(f"task {task_id!r} is not RUNNING (is {t.status.value})")
            target = TaskStatus.SUCCEEDED if success else TaskStatus.FAILED
            t.transition(target)
            # Re-evaluate dependents
            self.evaluate_all()
            return t

    def fail(self, task_id: str) -> Task:
        return self.complete(task_id, success=False)

    def succeed(self, task_id: str) -> Task:
        return self.complete(task_id, success=True)

    def prioritize(self, task_id: str, priority: str) -> Task:
        try:
            prio = TaskPriority(priority)
        except ValueError as exc:
            raise TaskQueueError(f"invalid priority {priority!r}") from exc
        with self._lock:
            t = self.get(task_id)
            t.priority = prio
            t.touch()
            return t

    def reorder(self, ordered_ids: List[str]) -> None:
        with self._lock:
            if set(ordered_ids) != set(self._tasks.keys()):
                raise TaskQueueError("reorder must contain exactly all task ids")
            self._order = list(ordered_ids)

    def increment_attempts(self, task_id: str) -> Task:
        with self._lock:
            t = self.get(task_id)
            t.attempts += 1
            t.touch()
            return t

    # -- Persistence ------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "tasks": {tid: t.to_dict() for tid, t in self._tasks.items()},
                "order": list(self._order),
            }

    def save_to_file(self, path: str) -> None:
        data = self.to_dict()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def load_from_file(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            raise TaskQueueError(f"file not found: {path}")
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "tasks" not in data:
            raise TaskQueueError("task queue file must contain 'tasks' mapping")
        with self._lock:
            self._tasks.clear()
            self._order.clear()
            for tid, tdata in data["tasks"].items():
                t = Task.from_dict(tdata)
                self._tasks[tid] = t
            self._order = list(data.get("order", list(self._tasks.keys())))
            # Ensure order contains all tasks
            for tid in self._tasks:
                if tid not in self._order:
                    self._order.append(tid)

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._order.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._tasks)

    def __contains__(self, task_id: str) -> bool:
        with self._lock:
            return task_id in self._tasks
