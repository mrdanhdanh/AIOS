"""Tests for :mod:`aios.core.container`."""

from __future__ import annotations

import threading

import pytest

from aios.core.container import Container, ContainerError, Lifetime, Scope


class DummyService:
    pass


class DummyImpl(DummyService):
    pass


class AnotherImpl(DummyService):
    pass


class TestRegistration:
    """Verify service registration."""

    def test_register_with_implementation(self):
        c = Container()
        c.register(DummyService, DummyImpl)
        assert c.is_registered(DummyService)

    def test_register_with_factory(self):
        c = Container()
        c.register(DummyService, factory=lambda: DummyImpl())
        assert c.is_registered(DummyService)

    def test_register_needs_impl_or_factory(self):
        c = Container()
        with pytest.raises(ContainerError, match="implementation or factory"):
            c.register(DummyService)

    def test_unregister(self):
        c = Container()
        c.register(DummyService, DummyImpl)
        c.unregister(DummyService)
        assert not c.is_registered(DummyService)


class TestSingletonLifetime:
    """Verify singleton behavior."""

    def test_same_instance(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SINGLETON)
        a = c.resolve(DummyService)
        b = c.resolve(DummyService)
        assert a is b

    def test_different_types(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SINGLETON)
        c.register(str, factory=lambda: "hello")
        a = c.resolve(DummyService)
        b = c.resolve(str)
        assert a is not b


class TestScopedLifetime:
    """Verify scoped behavior."""

    def test_same_instance_within_scope(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SCOPED)
        with c.create_scope() as scope:
            a = scope.resolve(DummyService)
            b = scope.resolve(DummyService)
            assert a is b

    def test_different_instances_across_scopes(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SCOPED)
        with c.create_scope() as s1:
            a = s1.resolve(DummyService)
        with c.create_scope() as s2:
            b = s2.resolve(DummyService)
        assert a is not b

    def test_scoped_without_scope_raises(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SCOPED)
        with pytest.raises(ContainerError, match="requires a scope"):
            c.resolve(DummyService)


class TestTransientLifetime:
    """Verify transient behavior."""

    def test_new_instance_every_time(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.TRANSIENT)
        a = c.resolve(DummyService)
        b = c.resolve(DummyService)
        assert a is not b


class TestResolution:
    """Verify resolution errors."""

    def test_unregistered_raises(self):
        c = Container()
        with pytest.raises(ContainerError, match="No registration"):
            c.resolve(DummyService)


class TestFactory:
    """Verify factory registration."""

    def test_factory_called(self):
        counter = {"n": 0}

        def make():
            counter["n"] += 1
            return DummyImpl()

        c = Container()
        c.register(DummyService, factory=make, lifetime=Lifetime.TRANSIENT)
        c.resolve(DummyService)
        c.resolve(DummyService)
        assert counter["n"] == 2


class TestThreadSafety:
    """Verify concurrent resolution."""

    def test_concurrent_singleton(self):
        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SINGLETON)
        results = []

        def resolve():
            results.append(c.resolve(DummyService))

        threads = [threading.Thread(target=resolve) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 10
        assert all(r is results[0] for r in results)


class TestMockInjection:
    """Verify service can be replaced with a mock (TASK-003 DoD: mock injection)."""

    def test_mock_overrides_real_implementation(self):
        from unittest.mock import Mock

        c = Container()
        c.register(DummyService, DummyImpl, Lifetime.SINGLETON)
        real = c.resolve(DummyService)
        assert isinstance(real, DummyImpl)

        mock = Mock(spec=DummyService)
        c.unregister(DummyService)
        c.register(DummyService, factory=lambda: mock, lifetime=Lifetime.SINGLETON)
        resolved = c.resolve(DummyService)
        assert resolved is mock
        # verify mock behaves as DummyService (spec mock) and can be reconfigured
        mock2 = Mock()
        mock2.hello.return_value = "mocked"
        c.unregister(DummyService)
        c.register(DummyService, factory=lambda: mock2, lifetime=Lifetime.SINGLETON)
        assert c.resolve(DummyService).hello() == "mocked"

    def test_mock_factory_transient_gives_mock_each_time(self):
        from unittest.mock import Mock

        c = Container()
        mock_a = Mock(spec=DummyService)
        mock_b = Mock(spec=DummyService)
        calls = [mock_a, mock_b]

        c.register(DummyService, factory=lambda: calls.pop(0), lifetime=Lifetime.TRANSIENT)
        assert c.resolve(DummyService) is mock_a
        assert c.resolve(DummyService) is mock_b

    def test_mock_in_scoped_scope(self):
        from unittest.mock import Mock

        c = Container()
        mock = Mock(spec=DummyService)
        c.register(DummyService, factory=lambda: mock, lifetime=Lifetime.SCOPED)
        with c.create_scope() as scope:
            assert scope.resolve(DummyService) is mock
            assert scope.resolve(DummyService) is mock
