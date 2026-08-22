"""Durable persistence fallback for Kill Switch (TASK-068).

TASK-066 (Durable) is not yet present in this workspace, so this module
provides an in-memory ``LocalDurablePersistence`` that satisfies the durable
contract: **verified state is never destroyed by a halt/drain**. A real durable
backend (T066) can be plugged in via the ``DurablePersistence`` interface
(see ``integration.build_durable_persistence``).
"""

from __future__ import annotations

from typing import Any, Dict, List


class DurablePersistence:
    """Interface a durable store must satisfy (T066-compatible)."""

    def persist(self, context_id: str, state: Dict[str, Any]) -> List[str]:
        raise NotImplementedError

    def persist_verified(self, key: str, state: Dict[str, Any]) -> None:
        raise NotImplementedError

    def get_state(self, context_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def get_verified(self, key: str) -> Dict[str, Any]:
        raise NotImplementedError

    def list_keys(self) -> List[str]:
        raise NotImplementedError


class LocalDurablePersistence(DurablePersistence):
    """In-memory durable stand-in.

    Working (in-flight) state and verified state live in separate namespaces so
    a halt/drain can never overwrite or delete already-verified state.
    """

    def __init__(self) -> None:
        self._working: Dict[str, Dict[str, Any]] = {}
        self._verified: Dict[str, Dict[str, Any]] = {}

    def persist(self, context_id: str, state: Dict[str, Any]) -> List[str]:
        self._working[context_id] = dict(state)
        return [context_id]

    def persist_verified(self, key: str, state: Dict[str, Any]) -> None:
        self._verified[key] = dict(state)

    def get_state(self, context_id: str) -> Dict[str, Any]:
        return dict(self._working.get(context_id, {}))

    def get_verified(self, key: str) -> Dict[str, Any]:
        return dict(self._verified.get(key, {}))

    def list_keys(self) -> List[str]:
        return list(self._working.keys())
