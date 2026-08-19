"""Regression Gate (Rule 7).

Before a task may PASS, the tests of its entire dependency closure must run and
pass. Any failure inside the closure BLOCKS the task.
"""

from .runner import (
    RegressionError,
    RegressionOutcome,
    RegressionResult,
    RegressionRunner,
)

__all__ = [
    "RegressionError",
    "RegressionOutcome",
    "RegressionResult",
    "RegressionRunner",
]
