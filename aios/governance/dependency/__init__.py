"""Dependency Graph (Rule 2).

Every task declares its dependencies. A task is only ``READY`` when all tasks in
its (transitive) dependency closure are in the ``PASS`` state. Cycles are
detected and block the offending tasks.
"""

from .graph import DependencyGraph, CycleError

__all__ = ["DependencyGraph", "CycleError"]
