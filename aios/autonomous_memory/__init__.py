"""Autonomous Memory (TASK-057).

Controlled failure/goal memory as a *capability* on the existing Memory (T007)
— not a second memory system. Entries carry provenance-validated evidence
refs, a trust/verification guard (INV-034), deterministic retention, scoped
access, and an autonomy-gated write path that consumes the Autonomy Governor
(T054) decision. No AutonomousMemoryStore/VectorDB/KnowledgeDB/Retriever.
"""

from aios.autonomous_memory.contracts import (
    FailureMemoryEntry,
    GoalMemoryEntry,
    MemoryScope,
    TrustStatus,
    VerificationStatus,
)
from aios.autonomous_memory.controller import MemoryController
from aios.autonomous_memory.retention import RetentionPolicy

__all__ = [
    "FailureMemoryEntry",
    "GoalMemoryEntry",
    "MemoryScope",
    "TrustStatus",
    "VerificationStatus",
    "MemoryController",
    "RetentionPolicy",
]
