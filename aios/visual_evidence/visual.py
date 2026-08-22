"""Visual Evidence — capture, UI state contract, visual regression (TASK-080).

* ``VisualCapture`` — captures a UI state (screenshot bytes / DOM snapshot) and
  produces a deterministic ``ui_state_hash`` (same state + same config -> same hash).
* ``UIStateContract`` — defines the set of valid UI states and an approved
  baseline (baseline changes require evidence/approval).
* ``VisualRegression`` — diffs a capture against the baseline; exceeding the
  threshold flags regression (fail-closed: never auto-pass).
* ``VisualEvidence`` — binds a capture to the provenance chain (T001 Rule 5).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


class VisualError(Exception):
    """Raised on visual contract / regression violations (fail-closed)."""


def sha256(content: bytes | str) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


@dataclass
class VisualEvidence:
    """A captured visual state bound to provenance."""

    capture_id: str
    ui_state_hash: str
    baseline_ref: str
    diff_score: float
    regression: bool
    evidence_ref: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capture_id": self.capture_id,
            "ui_state_hash": self.ui_state_hash,
            "baseline_ref": self.baseline_ref,
            "diff_score": self.diff_score,
            "regression": self.regression,
            "evidence_ref": self.evidence_ref,
            "notes": list(self.notes),
        }


class VisualCapture:
    """Captures a UI state deterministically."""

    def capture(self, state: bytes | str, config: str = "default") -> tuple[str, str]:
        """Return (ui_state_hash, normalized_repr) for a UI state."""
        norm = state if isinstance(state, str) else state.decode("utf-8", "replace")
        ui_state_hash = sha256(f"{config}|{norm}")
        return ui_state_hash, norm

    def capture_dom(self, dom: str, config: str = "default") -> tuple[str, str]:
        return self.capture(dom, config)


class UIStateContract:
    """Defines valid UI states and an approved baseline."""

    def __init__(self, valid_states: Optional[Sequence[str]] = None) -> None:
        self._valid_states = set(valid_states or [])
        self._baseline: dict[str, str] = {}  # state_name -> ui_state_hash
        self._approved: set[str] = set()

    def is_valid_state(self, state_name: str) -> bool:
        return state_name in self._valid_states

    def approve_baseline(self, state_name: str, ui_state_hash: str,
                         evidence_ref: str = "") -> None:
        """Approve a baseline (requires provenance evidence)."""
        if not evidence_ref:
            raise VisualError("baseline approval requires evidence_ref")
        if self._valid_states and state_name not in self._valid_states:
            raise VisualError(f"state {state_name} not in UI State Contract")
        self._baseline[state_name] = ui_state_hash
        self._approved.add(state_name)

    def baseline_hash(self, state_name: str) -> Optional[str]:
        return self._baseline.get(state_name)

    def is_approved(self, state_name: str) -> bool:
        return state_name in self._approved

    def change_baseline(self, state_name: str, ui_state_hash: str,
                        evidence_ref: str = "") -> None:
        """Change a baseline only with evidence/approval (fail-closed)."""
        if not self.is_approved(state_name):
            raise VisualError(f"baseline {state_name} not approved; approve first")
        if not evidence_ref:
            raise VisualError("baseline change requires evidence_ref")
        self._baseline[state_name] = ui_state_hash


class VisualRegression:
    """Diffs a capture against an approved baseline (fail-closed)."""

    def __init__(self, threshold: float = 0.05) -> None:
        self.threshold = threshold

    def diff(self, capture_hash: str, baseline_hash: str) -> float:
        """Return a normalized diff score in [0, 1]."""
        if capture_hash == baseline_hash:
            return 0.0
        # Hamming-style distance over hex digits -> normalized score.
        pairs = zip(capture_hash, baseline_hash)
        diff_bits = sum(1 for a, b in pairs if a != b)
        return diff_bits / max(len(capture_hash), 1)

    def evaluate(self, capture_hash: str, baseline_hash: str,
                 state_name: str = "", evidence_ref: str = "") -> VisualEvidence:
        if not baseline_hash:
            raise VisualError(f"no approved baseline for {state_name or 'state'}")
        score = self.diff(capture_hash, baseline_hash)
        regression = score > self.threshold
        notes = []
        if regression:
            notes.append("visual regression exceeds threshold -> flag (fail-closed)")
        return VisualEvidence(
            capture_id=f"cap-{capture_hash[:8]}",
            ui_state_hash=capture_hash,
            baseline_ref=baseline_hash,
            diff_score=score,
            regression=regression,
            evidence_ref=evidence_ref,
            notes=notes,
        )
