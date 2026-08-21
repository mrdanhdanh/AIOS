"""Context optimizer contracts — priority levels and context items."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class ContextPriority(IntEnum):
    """Context priority levels P0-P6. Lower number = higher priority."""
    P0_SYSTEM = 0      # System instructions — never dropped
    P1_CRITICAL = 1    # Critical context — never dropped
    P2_TASK = 2        # Current task context
    P3_MEMORY = 3      # Retrieved memory
    P4_HISTORY = 4     # Conversation history
    P5参考资料 = 5      # Reference material
    P6_LOW = 6         # Low priority — first to drop

    @property
    def never_drop(self) -> bool:
        """P0 and P1 are never dropped."""
        return self.value <= 1


@dataclass
class ContextItem:
    """A single context item."""

    item_id: str
    priority: ContextPriority
    content: str
    token_count: int = 0
    source: str = ""
    provenance: list[str] = field(default_factory=list)
    expired: bool = False
    superseded: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.token_count == 0:
            self.token_count = max(1, len(self.content.split()))

    @property
    def is_valid(self) -> bool:
        return not self.expired and not self.superseded

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "priority": self.priority.value,
            "content": self.content,
            "token_count": self.token_count,
            "source": self.source,
            "provenance": self.provenance,
            "expired": self.expired,
            "superseded": self.superseded,
        }


@dataclass
class OptimizedContext:
    """Result of context optimization."""

    items: list[ContextItem] = field(default_factory=list)
    total_tokens: int = 0
    budget: int = 0
    dropped_count: int = 0
    compressed_count: int = 0
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_count": len(self.items),
            "total_tokens": self.total_tokens,
            "budget": self.budget,
            "dropped_count": self.dropped_count,
            "compressed_count": self.compressed_count,
            "provenance": self.provenance,
        }
