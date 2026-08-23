"""Runtime-utilization governance gate (anti-loophole check).

Closes the TASK-222 loophole: a deliverable may be wrapped in governance
artifacts yet never actually exercise AIOS. This gate FAILS (fail-closed) any
task that declares ``Demonstrates-AIOS: true`` in its spec but whose
``implementation/`` shows no real AIOS usage and no AIOS-produced evidence.
"""

from .checker import RuntimeUtilizationCheck, check

__all__ = ["RuntimeUtilizationCheck", "check"]
