"""Deterministic-first routing (Rule 4 / T001).

The LLM is only invoked as a fallback when the deterministic control path is
INSUFFICIENT. :meth:`DeterministicRouter.route` returns the policy-driven
:class:`~aios.model_router.contracts.ModelRoute` together with the number of LLM
calls made (``0`` for SUFFICIENT intents, ``1`` for INSUFFICIENT with fallback).
"""

from __future__ import annotations

from typing import Callable, Optional, Tuple

from aios.governance.deterministic import DeterministicControlPath, Request
from aios.model_router.contracts import ModelRoute, RoutingPolicy
from aios.model_router.router import ModelRouter


class DeterministicRouter:
    """Routes an intent using the deterministic control path first."""

    def __init__(
        self,
        model_router: ModelRouter,
        llm_fallback: Optional[Callable[[str], str]] = None,
        validator: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self._mr = model_router
        self._path = DeterministicControlPath(llm_fallback=llm_fallback, validator=validator)

    def route(
        self,
        intent: str,
        policy: RoutingPolicy = RoutingPolicy.BALANCED,
        **kwargs: object,
    ) -> Tuple[ModelRoute, int]:
        # Deterministic-first: LLM only on INSUFFICIENT (Rule 4).
        self._path.execute(Request(text=intent))
        llm_call_count = self._path.llm_call_count
        model_route = self._mr.route(intent, policy, **kwargs)
        return model_route, llm_call_count
