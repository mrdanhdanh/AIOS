"""Autonomous Scheduler (TASK-062).

A scheduler layer for Autonomous Goals: activates a goal / workflow by schedule
(cron) or trigger (event / manual) in an autonomy-aware, fail-closed way.
Schedule ≠ Plan ≠ Execute: the Scheduler triggers activation, the Planner/Goal
Engine defines content, and the Governor (T054) decides whether activation is
*allowed*.
"""

from aios.autonomous_scheduler.contracts import ScheduleEntry, TriggerType
from aios.autonomous_scheduler.scheduler import Scheduler, SchedulerGate

__all__ = [
    "ScheduleEntry",
    "TriggerType",
    "Scheduler",
    "SchedulerGate",
]
