"""Tests for :mod:`aios.core.events`."""

from __future__ import annotations

import pytest

from aios.core.events import Event, EventBus


class GreetingEvent(Event):
    def __init__(self, message: str) -> None:
        self.message = message


class NumberEvent(Event):
    def __init__(self, value: int) -> None:
        self.value = value


class TestPublishSubscribe:
    """Verify basic pub/sub."""

    def test_subscriber_receives_event(self):
        bus = EventBus()
        received = []

        @bus.on(GreetingEvent)
        def handler(e: GreetingEvent):
            received.append(e.message)

        bus.publish(GreetingEvent("hello"))
        assert received == ["hello"]

    def test_multiple_subscribers(self):
        bus = EventBus()
        received = []

        @bus.on(GreetingEvent)
        def h1(e: GreetingEvent):
            received.append("h1")

        @bus.on(GreetingEvent)
        def h2(e: GreetingEvent):
            received.append("h2")

        bus.publish(GreetingEvent("x"))
        assert received == ["h1", "h2"]

    def test_different_event_types(self):
        bus = EventBus()
        greetings = []
        numbers = []

        @bus.on(GreetingEvent)
        def on_greet(e: GreetingEvent):
            greetings.append(e.message)

        @bus.on(NumberEvent)
        def on_num(e: NumberEvent):
            numbers.append(e.value)

        bus.publish(GreetingEvent("hi"))
        bus.publish(NumberEvent(42))
        assert greetings == ["hi"]
        assert numbers == [42]


class TestOrdering:
    """Verify dispatch order matches registration order."""

    def test_registration_order_preserved(self):
        bus = EventBus()
        order = []

        @bus.on(GreetingEvent)
        def first(e):
            order.append(1)

        @bus.on(GreetingEvent)
        def second(e):
            order.append(2)

        @bus.on(GreetingEvent)
        def third(e):
            order.append(3)

        bus.publish(GreetingEvent("x"))
        assert order == [1, 2, 3]


class TestErrorHandling:
    """Verify subscriber errors don't break dispatch."""

    def test_error_logged_dispatch_continues(self):
        bus = EventBus()
        received = []

        @bus.on(GreetingEvent)
        def bad(e):
            raise ValueError("oops")

        @bus.on(GreetingEvent)
        def good(e):
            received.append("ok")

        bus.publish(GreetingEvent("x"))
        assert received == ["ok"]


class TestProgrammaticSubscription:
    """Verify non-decorator subscribe/unsubscribe."""

    def test_subscribe(self):
        bus = EventBus()
        received = []
        bus.subscribe(GreetingEvent, lambda e: received.append(e.message))
        bus.publish(GreetingEvent("hi"))
        assert received == ["hi"]

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        handler = lambda e: received.append(e.message)
        bus.subscribe(GreetingEvent, handler)
        bus.unsubscribe(GreetingEvent, handler)
        bus.publish(GreetingEvent("hi"))
        assert received == []


class TestSubscriberCount:
    """Verify subscriber counting."""

    def test_count(self):
        bus = EventBus()
        assert bus.subscriber_count(GreetingEvent) == 0
        bus.subscribe(GreetingEvent, lambda e: None)
        assert bus.subscriber_count(GreetingEvent) == 1


class TestClear:
    """Verify clearing subscribers."""

    def test_clear_specific(self):
        bus = EventBus()
        bus.subscribe(GreetingEvent, lambda e: None)
        bus.subscribe(NumberEvent, lambda e: None)
        bus.clear(GreetingEvent)
        assert bus.subscriber_count(GreetingEvent) == 0
        assert bus.subscriber_count(NumberEvent) == 1

    def test_clear_all(self):
        bus = EventBus()
        bus.subscribe(GreetingEvent, lambda e: None)
        bus.subscribe(NumberEvent, lambda e: None)
        bus.clear()
        assert bus.subscriber_count(GreetingEvent) == 0
        assert bus.subscriber_count(NumberEvent) == 0
