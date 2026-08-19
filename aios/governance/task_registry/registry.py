"""Task Registry — Rule 1 (immutable, unique, never-reused, never-deleted)."""
import re
from .schema import TaskRecord

_ID_RE = re.compile(r"^TASK-\d+$")


class RegistryError(Exception):
    pass


class TaskRegistry:
    def __init__(self):
        self._tasks = {}  # id -> TaskRecord  (intentionally no delete API)

    def create_task(self, task_id, title, milestone="UNKNOWN", dependencies=None, created_at=None):
        if not _ID_RE.match(task_id):
            raise RegistryError(f"invalid task id: {task_id!r}")
        if task_id in self._tasks:
            # Rule 1: ID already exists -> reject reuse
            raise RegistryError(f"task id {task_id} already exists (immutable; never reuse)")
        rec = TaskRecord(
            task_id=task_id,
            title=title,
            milestone=milestone,
            dependencies=list(dependencies or []),
            created_at=created_at,
        )
        self._tasks[task_id] = rec
        return rec

    def get(self, task_id):
        if task_id not in self._tasks:
            raise RegistryError(f"unknown task id: {task_id}")
        return self._tasks[task_id]

    def has(self, task_id):
        return task_id in self._tasks

    def deprecate(self, task_id):
        """Wrong tasks are DEPRECATED, never deleted (Rule 1)."""
        self.get(task_id).status = "DEPRECATED"

    def all(self):
        return list(self._tasks.values())

    def __len__(self):
        return len(self._tasks)
