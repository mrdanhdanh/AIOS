"""Contract tests for Kill Switch (TASK-068)."""

from __future__ import annotations

import pytest

from aios.kill_switch.contracts import (
    HaltScope,
    HaltSignal,
    HaltSource,
    HaltViolation,
)


def test_halt_source_values():
    assert HaltSource.MANUAL.value == "manual"
    assert HaltSource.POLICY.value == "policy"
    assert HaltSource.SAFETY.value == "safety"


def test_halt_scope_values():
    assert HaltScope.GLOBAL.value == "global"
    assert HaltScope.GOAL.value == "goal"
    assert HaltScope.LOOP.value == "loop"


def test_signal_requires_nonempty_reason():
    with pytest.raises(ValueError):
        HaltSignal(
            source=HaltSource.MANUAL,
            scope=HaltScope.GLOBAL,
            issued_at="2026-08-22T00:00:00+00:00",
            reason="",
        )


def test_signal_canonical_is_deterministic():
    a = HaltSignal(
        source=HaltSource.MANUAL,
        scope=HaltScope.GLOBAL,
        issued_at="2026-08-22T00:00:00+00:00",
        reason="emergency",
        signal_id="s1",
    )
    b = HaltSignal(
        source=HaltSource.MANUAL,
        scope=HaltScope.GLOBAL,
        issued_at="2026-08-22T00:00:00+00:00",
        reason="emergency",
        signal_id="s1",
    )
    assert a.canonical() == b.canonical()


def test_halt_violation_is_exception():
    assert issubclass(HaltViolation, Exception)
