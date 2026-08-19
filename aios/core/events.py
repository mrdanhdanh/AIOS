"""In-process event bus with typed events and synchronous dispatch.

Events are dispatched in registration order.  If a subscriber raises, the
bus logs the error and continues dispatching to remaining subscribers.

Example::

    from aios.core.events import EventBus, Event

    bus = EventBus()

    @bus.on(MyEvent)
    def handle(event: MyEvent):
        print(event.data)

    bus.publish(MyEvent(data="hello"))
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

__all__ = ["EventBus", "Event", "EventHandler"]

E = TypeVar("E", bound="Event")


@dataclass(frozen=True)
class Event:
    """Base class for all events."""

    pass


class EventHandler:
    """Wraps a subscriber callback with metadata."""

    __slots__ = ("callback", "event_type", "_order")

    def __init__(
        self,
        callback: Callable[[Any], None],
        event_type: Type[Event],
        order: int = 0,
    ) -> None:
        self.callback = callback
        self.event_type = event_type
        self._order = order

    def __repr__(self) -> str:
        return (
            f"EventHandler({self.callback.__name__}, "
            f"{self.event_type.__name__}, order={self._order})"
        )


class EventBus:
    """In-process publish/subscribe event bus.

    Thread-safe: publish and subscribe are guarded by a lock.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[EventHandler]] = defaultdict(
            list
        )
        self._order_counter = 0
        self._lock = threading.Lock()

    def on(self, event_type: Type[E]) -> Callable:
        """Decorator to subscribe to an event type.

        Example::

            @bus.on(MyEvent)
            def handler(event: MyEvent):
                ...
        """

        def decorator(fn: Callable[[E], None]) -> Callable[[E], None]:
            with self._lock:
                handler = EventHandler(
                    callback=fn,
                    event_type=event_type,
                    order=self._order_counter,
                )
                self._order_counter += 1
                self._subscribers[event_type].append(handler)
            return fn

        return decorator

    def subscribe(
        self, event_type: Type[E], handler: Callable[[E], None]
    ) -> None:
        """Programmatic subscription (non-decorator)."""
        with self._lock:
            h = EventHandler(
                callback=handler,
                event_type=event_type,
                order=self._order_counter,
            )
            self._order_counter += 1
            self._subscribers[event_type].append(h)

    def unsubscribe(
        self, event_type: Type[E], handler: Callable[[E], None]
    ) -> None:
        """Remove a specific handler for an event type."""
        with self._lock:
            handlers = self._subscribers.get(event_type, [])
            self._subscribers[event_type] = [
                h for h in handlers if h.callback is not handler
            ]

    def publish(self, event: Event) -> None:
        """Dispatch an event to all registered subscribers.

        Subscribers are called in registration order.  If a subscriber
        raises, the error is logged and dispatch continues.
        """
        with self._lock:
            handlers = list(self._subscribers.get(type(event), []))

        for handler in handlers:
            try:
                handler.callback(event)
            except Exception:
                logger.warning(
                    "Subscriber %s raised for event %s",
                    handler.callback.__name__,
                    type(event).__name__,
                    exc_info=True,
                )

    def subscriber_count(self, event_type: Type[Event]) -> int:
        """Return the number of subscribers for an event type."""
        with self._lock:
            return len(self._subscribers.get(event_type, []))

    def clear(self, event_type: Optional[Type[Event]] = None) -> None:
        """Remove all subscribers (or only for a specific event type)."""
        with self._lock:
            if event_type is None:
                self._subscribers.clear()
            else:
                self._subscribers.pop(event_type, None)
