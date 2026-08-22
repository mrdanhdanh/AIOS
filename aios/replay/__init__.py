"""RenderReplay — deterministic record/replay harness (TASK-079, M11).

Records a normalized execution run (inputs + evidence snapshot + verifier
state) and replays it deterministically to reproduce the original verdict for
audit/debug. Does NOT replace the runtime; it wraps Harness (T030/T032) +
Evidence (T001) + Integrity (T078).

Layering: ``unknown`` (infra) layer — stdlib + ``aios.governance.evidence``
+ ``aios.harness`` + ``aios.verification_integrity`` only.
"""

from __future__ import annotations

from .replay import (
    Recorder,
    Replayer,
    ReplaySession,
    ReplayError,
)

__all__ = ["Recorder", "Replayer", "ReplaySession", "ReplayError"]
