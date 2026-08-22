"""AIOS Cost Meter — per-step/goal cost metering + budget guard (TASK-075).

Provider-agnostic, fail-closed. When cumulative cost exceeds the budget the
meter emits :class:`CostExceeded` so the caller can escalate/stop. If
``aios.autonomy_safety`` (SAFE_STOP) or ``aios.kill_switch`` were present they
would be invoked here; they are absent in this codebase, so the signal is raised.
"""

from aios.cost_meter.cost_meter import CostExceeded, CostMeter, CostRecord
from aios.cost_meter.perf_budget import PerformanceBudget, SLO, SLOViolation

__all__ = [
    "CostExceeded",
    "CostMeter",
    "CostRecord",
    "PerformanceBudget",
    "SLO",
    "SLOViolation",
]
