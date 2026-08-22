"""Autonomous Harness Loop (TASK-099, M15).

Self-testing loop: schedule/trigger harness run (T062), run harness chain
(T030/T032/T078/T079/T089/T091), detect deviation (T094), trigger remediation
(T095-T098) autonomy-gated (T054/T067), loop evidence (provenance).
"""

from aios.autonomous_harness_loop.loop import (
    HarnessLoopEngine,
    HarnessLoopRun,
    LoopVerdict,
)

__all__ = [
    "HarnessLoopEngine",
    "HarnessLoopRun",
    "LoopVerdict",
]
