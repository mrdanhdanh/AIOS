"""TaskRecord schema (Rule 1: immutable, never-reused, never-deleted)."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TaskRecord:
    task_id: str
    title: str
    milestone: str = "UNKNOWN"
    status: str = "PLANNED"  # PLANNED | DEPRECATED (never deleted)
    dependencies: List[str] = field(default_factory=list)
    created_at: Optional[str] = None

    def is_active(self) -> bool:
        return self.status != "DEPRECATED"
