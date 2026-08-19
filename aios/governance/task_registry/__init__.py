"""Task Registry (Rule 1).

The registry is the single source of truth for task identity. Task IDs are
unique, immutable and never reused. A task that must be removed is marked
``DEPRECATED`` rather than deleted, so its ID can never be reused.
"""

from .models import Task, TaskStatus
from .registry import TaskRegistry, RegistryError

__all__ = ["Task", "TaskStatus", "TaskRegistry", "RegistryError"]
