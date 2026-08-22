"""Durable Execution 1.0 (TASK-066).

State durability, checkpointing and crash-safe resume for the AIOS runtime.
Integrates with the runtime state store (T065) and autonomous recovery (T055)
via their public interfaces -- no parallel execution store is created.

Layering: ``durable`` is a runtime-level durability concern. It imports the
runtime state store and recovery contracts (peer packages) only -- never
``aios.agents``.
"""

from __future__ import annotations

from .checkpoint import Checkpoint
from .idempotency import IdempotencyGuard, StepOutcome
from .resume import ResumeError, ResumeProtocol
from .store import CheckpointStore

__all__ = [
    "Checkpoint",
    "CheckpointStore",
    "ResumeProtocol",
    "ResumeError",
    "IdempotencyGuard",
    "StepOutcome",
]
