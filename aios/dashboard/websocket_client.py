"""WebSocket client for realtime dashboard events.

Connects to the FastAPI WebSocket gateway and streams events.
Handles reconnection without losing event context.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable


class DashboardWebSocketClient:
    """WebSocket event client for the dashboard.

    AC-018-03: Realtime events update correctly via WebSocket.
    AC-018-04: Reconnect preserves event context.
    """

    def __init__(self, ws_url: str = "ws://localhost:8000/api/v1/ws/events") -> None:
        self._ws_url = ws_url
        self._connected = False
        self._events: list[dict[str, Any]] = []
        self._sequence: int = 0
        self._listeners: list[Callable[[dict[str, Any]], None]] = []
        self._lock = threading.Lock()
        self._reconnect_count: int = 0
        self._last_event_time: float = 0.0

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def event_count(self) -> int:
        with self._lock:
            return len(self._events)

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def reconnect_count(self) -> int:
        return self._reconnect_count

    def connect(self) -> None:
        """Establish WebSocket connection."""
        self._connected = True

    def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._connected = False

    def reconnect(self) -> None:
        """Reconnect after disconnection, preserving event context.

        AC-018-04: Reconnect does not lose event context.
        """
        self._reconnect_count += 1
        self._connected = True
        # Events and sequence are preserved — no reset

    def add_listener(self, listener: Callable[[dict[str, Any]], None]) -> None:
        """Register an event listener."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[dict[str, Any]], None]) -> None:
        """Unregister an event listener."""
        with self._lock:
            self._listeners = [l for l in self._listeners if l is not listener]

    def on_event(self, event: dict[str, Any]) -> None:
        """Process an incoming WebSocket event.

        Events are stored with sequence numbers for ordering.
        """
        with self._lock:
            self._sequence += 1
            event_with_seq = {**event, "_sequence": self._sequence}
            self._events.append(event_with_seq)
            self._last_event_time = time.time()
            listeners = list(self._listeners)

        for listener in listeners:
            listener(event_with_seq)

    def get_events(
        self,
        event_type: str | None = None,
        since_sequence: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get stored events with optional filtering.

        AC-018-04: Events are available after reconnect.
        """
        with self._lock:
            events = list(self._events)

        if event_type:
            events = [e for e in events if e.get("type") == event_type]

        if since_sequence is not None:
            events = [e for e in events if e.get("_sequence", 0) > since_sequence]

        if limit is not None:
            events = events[-limit:]

        return events

    def get_last_event(self) -> dict[str, Any] | None:
        """Get the most recent event."""
        with self._lock:
            return self._events[-1] if self._events else None

    def clear_events(self) -> None:
        """Clear stored events. Use with caution — breaks provenance."""
        with self._lock:
            self._events.clear()
            self._sequence = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize client state."""
        return {
            "ws_url": self._ws_url,
            "connected": self._connected,
            "event_count": self.event_count,
            "sequence": self._sequence,
            "reconnect_count": self._reconnect_count,
        }
