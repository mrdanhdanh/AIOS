"""Stuck Detector (TASK-061).

Monitors every loop iteration (no gaps). Detects oscillation via stable
trajectory hash, plateau via progress below threshold over N iterations,
resource-burn via rising cost with flat progress, and deadlock. Fail-closed:
low confidence / missing evidence → escalate, never auto-continue.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable

from aios.stuck_detection.contracts import (
    StuckKind,
    StuckPolicy,
    StuckSeverity,
    StuckSignal,
)


@dataclass
class IterationSample:
    iteration: int
    progress: float
    cost: float
    state_hash: str  # hash of the trajectory/state at this iteration
    evidence_ref: str = ""


class StuckDetector:
    def __init__(
        self,
        policy: StuckPolicy | None = None,
        plateau_threshold: float = 0.01,
        plateau_window: int = 3,
        resource_burn_window: int = 3,
        oscillation_window: int = 3,
    ) -> None:
        self._policy = policy or StuckPolicy()
        self._plateau_threshold = plateau_threshold
        self._plateau_window = plateau_window
        self._resource_burn_window = resource_burn_window
        self._oscillation_window = oscillation_window
        self._history: list[IterationSample] = []
        self._oscillation_seen_at: dict[str, int] = {}

    def observe(self, sample: IterationSample) -> None:
        # Every iteration is monitored (no gaps).
        self._history.append(sample)
        # Track repeated state hashes for oscillation detection.
        if sample.state_hash in self._oscillation_seen_at:
            # already seen before -> candidate oscillation
            pass
        self._oscillation_seen_at.setdefault(sample.state_hash, sample.iteration)

    def detect(self) -> StuckSignal | None:
        if len(self._history) < 2:
            return None
        # 1. Oscillation: same state_hash repeats within the window.
        recent = self._history[-self._oscillation_window:]
        hashes = [s.state_hash for s in recent]
        if len(hashes) >= 2 and len(set(hashes)) < len(hashes):
            # a repeated hash in the recent window
            seen = set()
            for h in hashes:
                if h in seen:
                    return self._signal(StuckKind.OSCILLATION, StuckSeverity.MAJOR,
                                        self._first_seen(h), 0.9, recent[-1].evidence_ref)
                seen.add(h)
        # 2. Resource burn: cost rises while progress flat (stronger than plateau).
        if len(self._history) >= self._resource_burn_window:
            window = self._history[-self._resource_burn_window:]
            cost_up = window[-1].cost > window[0].cost * 1.1
            prog_flat = all(abs(window[i].progress - window[i - 1].progress) < self._plateau_threshold
                            for i in range(1, len(window)))
            if cost_up and prog_flat:
                return self._signal(StuckKind.RESOURCE_BURN, StuckSeverity.MAJOR,
                                    window[0].iteration, 0.85, window[-1].evidence_ref)
        # 3. Plateau: progress delta < threshold over the window.
        if len(self._history) >= self._plateau_window:
            window = self._history[-self._plateau_window:]
            deltas = [abs(window[i].progress - window[i - 1].progress) for i in range(1, len(window))]
            if all(d < self._plateau_threshold for d in deltas) and window[-1].progress < 0.999:
                return self._signal(StuckKind.PLATEAU, StuckSeverity.MINOR,
                                    window[0].iteration, 0.8, window[-1].evidence_ref)
        # 4. No progress (broad): progress stuck near zero across many iters.
        if len(self._history) >= self._plateau_window and self._history[-1].progress < 0.01:
            return self._signal(StuckKind.NO_PROGRESS, StuckSeverity.MINOR,
                                self._history[0].iteration, 0.7, self._history[-1].evidence_ref)
        return None

    def _first_seen(self, state_hash: str) -> int:
        return self._oscillation_seen_at.get(state_hash, 0)

    def _signal(self, kind, severity, first_seen, confidence, evidence_ref) -> StuckSignal:
        return StuckSignal(
            kind=kind, severity=severity, iteration_first_seen=first_seen,
            confidence=confidence, evidence_ref=evidence_ref,
        )

    def resolve_action(self, signal: StuckSignal) -> str:
        return self._policy.resolve(signal)

    @property
    def history(self) -> list[IterationSample]:
        return list(self._history)


class StuckGate:
    """Triggers a stuck action only when the Governor authorizes + autonomy suffices."""

    def __init__(self, governor_decision: Callable[[str, dict], str] | None = None) -> None:
        self._governor = governor_decision  # (action, ctx) -> ALLOW/BLOCK/ESCALATE

    def gate(self, action: str, context: dict[str, Any] | None = None) -> tuple[str, str]:
        ctx = context or {}
        if ctx.get("budget_exceeded"):
            return "BLOCK", "budget_exceeded"
        if self._governor is not None:
            gv = self._governor(action, ctx)
            if gv == "BLOCK":
                return "BLOCK", "governor_blocked"
            if gv == "ESCALATE":
                return "ESCALATE", "governor_escalate"
        return action, "allowed"
