"""Deterministic record/replay harness (TASK-079, M11).

* ``Recorder`` captures normalized inputs + evidence snapshot + verifier
  version/config and produces a ``recorded_inputs_hash``.
* ``Replayer`` re-runs with the same inputs via a supplied deterministic
  evaluator and compares the replay verdict to the original.
* ``ReplaySession`` records the outcome (matches_original / non-determinism).

Deterministic guarantee: same input + same verifier -> same verdict.
Fail-closed on mismatch: a differing replay is flagged, never auto-promoted.
No side-effects: replay never mutates production state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


class ReplayError(Exception):
    """Raised on replay contract violations (fail-closed)."""


def _norm(obj: Any) -> str:
    """Stable JSON serialization for deterministic hashing."""
    try:
        return json.dumps(obj, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return repr(obj)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class ReplaySession:
    """Outcome of a replay against an original recorded run."""

    original_run_id: str
    recorded_inputs_hash: str
    verifier_version: str
    verifier_config_hash: str
    replay_verdict: str
    original_verdict: str
    matches_original: bool
    evidence_ref: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_run_id": self.original_run_id,
            "recorded_inputs_hash": self.recorded_inputs_hash,
            "verifier_version": self.verifier_version,
            "verifier_config_hash": self.verifier_config_hash,
            "replay_verdict": self.replay_verdict,
            "original_verdict": self.original_verdict,
            "matches_original": self.matches_original,
            "evidence_ref": self.evidence_ref,
            "notes": list(self.notes),
        }


class Recorder:
    """Captures a normalized run for later deterministic replay."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def record(
        self,
        run_id: str,
        inputs: Any,
        evidence_snapshot: Any,
        verifier_version: str,
        verifier_config: str = "",
        original_verdict: str = "",
    ) -> str:
        """Store a normalized record; return recorded_inputs_hash."""
        norm_inputs = _norm(inputs)
        norm_ev = _norm(evidence_snapshot)
        recorded_inputs_hash = sha256(norm_inputs)
        self._records[run_id] = {
            "run_id": run_id,
            "inputs_norm": norm_inputs,
            "evidence_norm": norm_ev,
            "verifier_version": verifier_version,
            "verifier_config": verifier_config,
            "verifier_config_hash": sha256(f"{verifier_version}|{verifier_config}"),
            "recorded_inputs_hash": recorded_inputs_hash,
            "original_verdict": original_verdict,
        }
        return recorded_inputs_hash

    def get(self, run_id: str) -> dict[str, Any]:
        if run_id not in self._records:
            raise ReplayError(f"no recorded run {run_id}")
        return self._records[run_id]


class Replayer:
    """Replays a recorded run deterministically and checks for drift."""

    def __init__(self, recorder: Optional[Recorder] = None) -> None:
        self._recorder = recorder or Recorder()

    def replay(
        self,
        run_id: str,
        evaluator: Callable[[Any], str],
        evidence_ref: str = "",
    ) -> ReplaySession:
        """Re-run the recorded inputs through ``evaluator`` and compare."""
        rec = self._recorder.get(run_id)
        # Reconstruct normalized inputs from stored record (no mutation of prod).
        inputs = rec["inputs_norm"]
        replay_verdict = str(evaluator(inputs))
        matches = replay_verdict == rec["original_verdict"]
        notes: list[str] = []
        if not matches:
            notes.append("non-determinism detected: replay verdict != original")
        return ReplaySession(
            original_run_id=run_id,
            recorded_inputs_hash=rec["recorded_inputs_hash"],
            verifier_version=rec["verifier_version"],
            verifier_config_hash=rec["verifier_config_hash"],
            replay_verdict=replay_verdict,
            original_verdict=rec["original_verdict"],
            matches_original=matches,
            evidence_ref=evidence_ref,
            notes=notes,
        )
