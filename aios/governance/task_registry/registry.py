"""Task Registry implementation (Rule 1)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .models import Task, TaskStatus


class RegistryError(Exception):
    """Raised when a registry invariant would be violated."""


class TaskRegistry:
    """Single, authoritative task registry.

    Invariants (Rule 1):
      * IDs are unique.
      * IDs are immutable (a task record is never edited to change its id).
      * IDs are never reused, even after deprecation.
      * Tasks are never deleted; a removed task becomes ``DEPRECATED``.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._deprecated: set[str] = set()

    # ------------------------------------------------------------------ #
    # Mutations
    # ------------------------------------------------------------------ #
    def create_task(
        self,
        task_id: str,
        title: str,
        milestone: str = "",
        dependencies: Optional[Iterable[str]] = None,
        created_at: str = "",
    ) -> Task:
        """Create and register a new task.

        Raises :class:`RegistryError` if ``task_id`` already exists or has been
        deprecated (ID reuse is forbidden).
        """
        if task_id in self._tasks:
            raise RegistryError(
                f"Task ID '{task_id}' already exists; task IDs are immutable "
                f"and must never be reused."
            )
        if task_id in self._deprecated:
            raise RegistryError(
                f"Task ID '{task_id}' was deprecated and cannot be reused."
            )
        if dependencies:
            for dep in dependencies:
                if dep == task_id:
                    raise RegistryError(
                        f"Task '{task_id}' cannot depend on itself."
                    )
        task = Task(
            task_id=task_id,
            title=title,
            milestone=milestone,
            dependencies=list(dependencies or []),
            status=TaskStatus.PLANNED,
            created_at=created_at,
        )
        self._tasks[task_id] = task
        return task

    def deprecate(self, task_id: str) -> Task:
        """Mark a task as deprecated instead of deleting it.

        The ID is recorded so it can never be reused via :meth:`create_task`.
        """
        task = self.get(task_id)
        if task.status == TaskStatus.DEPRECATED:
            return task
        task.status = TaskStatus.DEPRECATED
        self._deprecated.add(task_id)
        return task

    def set_status(self, task_id: str, status: TaskStatus) -> Task:
        task = self.get(task_id)
        task.status = status
        return task

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        task = self.get(task_id)
        if depends_on == task_id:
            raise RegistryError(f"Task '{task_id}' cannot depend on itself.")
        if depends_on not in self._tasks:
            raise RegistryError(
                f"Cannot add dependency '{depends_on}': not registered."
            )
        if depends_on not in task.dependencies:
            task.dependencies.append(depends_on)

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    def get(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise RegistryError(f"Task '{task_id}' is not registered.")
        return self._tasks[task_id]

    def exists(self, task_id: str) -> bool:
        return task_id in self._tasks

    def is_deprecated(self, task_id: str) -> bool:
        return task_id in self._deprecated

    def list_all(self) -> List[Task]:
        return list(self._tasks.values())

    def ids(self) -> List[str]:
        return list(self._tasks.keys())
