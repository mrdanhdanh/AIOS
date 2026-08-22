"""Integration glue with T065 runtime state store and T055 recovery (TASK-066).

This module is the *only* place that reaches into peer packages. It converts a
runtime :class:`~aios.runtime.state.ExecutionState` into a durable
:class:`~aios.durable.checkpoint.Checkpoint` (reusing the runtime state-store
hash) and records resume activity as a T055 :class:`RecoveryAttempt` with
strategy ``RESUME``. No parallel execution store is created -- the runtime
``StateStore`` remains the source of truth for live execution state.

Layering: ``durable`` is a runtime-level durability concern; it imports the
runtime state store (peer) and recovery contracts (peer) only -- never
``aios.agents``.
"""

from __future__ import annotations

import hashlib
import json
from typing import List, Optional

from aios.autonomous_recovery.contracts import (
    FailureClass,
    RecoveryAttempt,
    RecoveryStrategy,
    RecoveryVerdict,
)
from aios.runtime.state import ExecutionState

from .checkpoint import Checkpoint


def runtime_state_hash(state: ExecutionState) -> str:
    """Stable integrity hash of a runtime ``ExecutionState`` (T065).

    Derived from ``ExecutionState.to_dict()`` (which is stable across calls,
    unlike ``to_checkpoint().content_hash`` that mints a fresh ``created_at``).
    This is the canonical ``state_hash`` reused by the durable checkpoint so
    durability stays consistent with the runtime state store (no parallel store).
    """
    return hashlib.sha256(
        json.dumps(state.to_dict(), sort_keys=True).encode()
    ).hexdigest()


def checkpoint_from_execution_state(
    state: ExecutionState,
    step_id: str,
    evidence_ref: str,
    verified: bool = True,
    created_at: Optional[str] = None,
) -> Checkpoint:
    """Derive a durable :class:`Checkpoint` from a runtime ``ExecutionState`` (T065).

    The ``state_hash`` reuses the runtime state representation so durability
    stays consistent with the runtime state store (no parallel store).
    """
    runtime_chk = state.to_checkpoint()
    return Checkpoint(
        execution_id=state.execution_id,
        step_id=step_id,
        state_hash=runtime_state_hash(state),
        verified=verified,
        created_at=created_at or state.updated_at or runtime_chk.created_at,
        evidence_ref=evidence_ref,
    )


def build_resume_attempt(
    execution_id: str,
    checkpoint: Checkpoint,
    outcome: RecoveryVerdict = RecoveryVerdict.RECOVERED,
    evidence: Optional[List[str]] = None,
) -> RecoveryAttempt:
    """Record a resume as a T055 :class:`RecoveryAttempt` (strategy=RESUME)."""
    return RecoveryAttempt(
        execution_id=execution_id,
        failure="execution_resume",
        classification=FailureClass.STATE,
        strategy=RecoveryStrategy.RESUME,
        policy_decision="durable_resume_protocol",
        pre_state={"checkpoint_id": checkpoint.checkpoint_id},
        action="resume_from_verified_checkpoint",
        post_state={
            "step_id": checkpoint.step_id,
            "state_hash": checkpoint.state_hash,
        },
        verification=f"verified={checkpoint.verified}",
        evidence=list(evidence or [checkpoint.evidence_ref]),
        outcome=outcome,
    )
