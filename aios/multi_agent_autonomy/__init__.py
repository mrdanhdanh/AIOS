"""Multi-Agent Autonomy — Delegation (TASK-059).

A delegation *capability* extending the existing Orchestrator (Agent Selector
/ Capability Router). It attenuates parent authority multi-dimensionally,
tracks anti-amplification budgets, and records a delegation provenance chain.
It is NOT a second control plane or mini broker.
"""

from aios.multi_agent_autonomy.contracts import (
    Authority,
    DelegateRequest,
    DelegateResponse,
    DelegationDecision,
)
from aios.multi_agent_autonomy.delegation import AuthorityAttenuator, DelegationManager

__all__ = [
    "Authority",
    "DelegateRequest",
    "DelegateResponse",
    "DelegationDecision",
    "AuthorityAttenuator",
    "DelegationManager",
]
