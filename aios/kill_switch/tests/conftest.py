"""Shared test fixtures for Kill Switch (TASK-068)."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from aios.kill_switch.contracts import DrainResult, HaltSignal, HaltScope, HaltSource


class FakeContext:
    """A compliant execution context (loop or goal) that respects the halt."""

    def __init__(
        self,
        context_id: str,
        context_type: str,
        in_flight: Dict[str, Any] | None = None,
        skip: bool = False,
    ) -> None:
        self.context_id = context_id
        self.context_type = context_type
        self._halted = False
        self._in_flight = in_flight or {}
        self._skip = skip  # if True, ignores the halt (tries to skip)
        self.drain_called = False
        self.on_halt_calls = 0

    def on_halt(self, signal: HaltSignal) -> None:
        self.on_halt_calls += 1
        if self._skip:
            return  # ignore -> skip the halt
        self._halted = True

    def is_halted(self) -> bool:
        return self._halted

    def drain(self) -> DrainResult:
        self.drain_called = True
        return DrainResult(
            context_id=self.context_id,
            context_type=self.context_type,
            drained=True,
            persisted_keys=[self.context_id],
            state={"in_flight": self._in_flight, "halted": self._halted},
        )


class FailingDrainContext(FakeContext):
    """A context whose drain raises (must not break fail-closed enforcement)."""

    def drain(self) -> DrainResult:
        raise RuntimeError("drain boom")


def make_signal(source: HaltSource, scope: HaltScope, reason: str, target_id: str = "") -> HaltSignal:
    return HaltSignal(
        source=source,
        scope=scope,
        issued_at="2026-08-22T00:00:00+00:00",
        reason=reason,
        signal_id=f"{source.value}-{scope.value}-{reason}",
        target_id=target_id,
    )


@pytest.fixture
def loop_ctx() -> FakeContext:
    return FakeContext("loop-1", "loop", in_flight={"step": 3})


@pytest.fixture
def goal_ctx() -> FakeContext:
    return FakeContext("goal-1", "goal", in_flight={"progress": 0.5})
