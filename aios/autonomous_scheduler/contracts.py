"""Autonomous Scheduler contracts (TASK-062)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TriggerType(str, Enum):
    CRON = "cron"
    EVENT = "event"
    MANUAL = "manual"


@dataclass
class ScheduleEntry:
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    trigger: TriggerType = TriggerType.MANUAL
    cron_expr: str = ""        # for CRON
    event_filter: str = ""     # for EVENT (e.g. topic/pattern)
    manual_token: str = ""     # for MANUAL (opaque token)
    autonomy_level_required: str = "supervised"
    enabled: bool = True
    next_fire: float = 0.0     # derived; durable across restart
    created_at: float = field(default_factory=time.time)
    last_fired: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "goal_id": self.goal_id,
            "trigger": self.trigger.value,
            "cron_expr": self.cron_expr,
            "event_filter": self.event_filter,
            "autonomy_level_required": self.autonomy_level_required,
            "enabled": self.enabled,
            "next_fire": self.next_fire,
        }
