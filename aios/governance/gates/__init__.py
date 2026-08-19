"""Unified Task Gate.

Converges the seven governance rules into a single pass/fail decision:

    Registry AND Dependency AND Architecture AND Lifecycle
    AND Evidence AND Test/Evaluate AND Regression  =>  DONE

else the task is BLOCKED.
"""

from .unified import GateComponent, GateResult, UnifiedTaskGate

__all__ = ["GateComponent", "GateResult", "UnifiedTaskGate"]
