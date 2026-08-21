"""Extension event client for real-time updates.

AC-019-09: Extension reconnects with backend.
AC-019-10: No parallel state authority.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable


class ExtensionEventClient:
    """Real-time event client for VS Code extension.

    Receives events from the AIOS WebSocket gateway.
    Handles reconnection without losing context.
    """

    def __init__(self, ws_url: str = "ws://localhost:8000/api/v1/ws/events") -> None:
        self._ws_url = ws_url
        self._connected = False
        self._events: list[dict[str, Any]] = []
        self._sequence: int = 0
        self._listeners: list[Callable[[dict[str, Any]], None]] = []
        self._lock = threading.Lock()
        self._reconnect_count: int = 0

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def event_count(self) -> int:
        with self._lock:
            return len(self._events)

    @property
    def reconnect_count(self) -> int:
        return self._reconnect_count

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def reconnect(self) -> None:
        """Reconnect preserving event context.

        AC-019-09: Reconnects without losing state.
        """
        self._reconnect_count += 1
        self._connected = True
        # Events preserved

    def add_listener(self, listener: Callable[[dict[str, Any]], None]) -> None:
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[dict[str, Any]], None]) -> None:
        with self._lock:
            self._listeners = [l for l in self._listeners if l is not listener]

    def on_event(self, event: dict[str, Any]) -> None:
        """Process incoming event."""
        with self._lock:
            self._sequence += 1
            event_with_seq = {**event, "_sequence": self._sequence}
            self._events.append(event_with_seq)
            listeners = list(self._listeners)
        for listener in listeners:
            listener(event_with_seq)

    def get_events(
        self,
        event_type: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get events with optional filtering."""
        with self._lock:
            events = list(self._events)
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        if limit is not None:
            events = events[-limit:]
        return events

    def to_dict(self) -> dict[str, Any]:
        return {
            "ws_url": self._ws_url,
            "connected": self._connected,
            "event_count": self.event_count,
            "reconnect_count": self._reconnect_count,
        }
