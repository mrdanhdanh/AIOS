"""AIOS agent roles (orchestrator / spec-writer / critic / reviewer).

These modules define the *contracts and responsibilities* of each agent role.
Per Rule 3 (Architecture Guard) they MUST NOT import execution primitives
(``subprocess``), provider adapters or filesystem adapters directly; they act
only through the governance/runtime interfaces supplied to them.
"""

from .orchestrator import Orchestrator
from .spec_writer import SpecWriter
from .critic import Critic
from .reviewer import Reviewer

__all__ = ["Orchestrator", "SpecWriter", "Critic", "Reviewer"]
