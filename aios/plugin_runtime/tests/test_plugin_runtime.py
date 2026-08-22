"""Tests for plugin runtime."""
from __future__ import annotations
import pytest
from aios.plugin_runtime.contracts import PluginSpec, PluginState
from aios.plugin_runtime.manifest import PluginManifest
from aios.plugin_runtime.runtime import PluginRuntime

class TestPluginRuntime:
    def test_register(self):
        rt = PluginRuntime()
        p = rt.register(PluginSpec(name="test"))
        assert p.name == "test"
    def test_load_enable_disable(self):
        rt = PluginRuntime()
        p = rt.register(PluginSpec(name="p1"))
        rt.load(p.plugin_id)
        assert p.state == PluginState.LOADED
        rt.enable(p.plugin_id)
        assert p.state == PluginState.ENABLED
        rt.disable(p.plugin_id)
        assert p.state == PluginState.DISABLED
    def test_not_found(self):
        rt = PluginRuntime()
        with pytest.raises(RuntimeError): rt.load("nonexistent")
    def test_list(self):
        rt = PluginRuntime()
        rt.register(PluginSpec(name="a")); rt.register(PluginSpec(name="b"))
        assert len(rt.list_plugins()) == 2
    def test_to_dict(self):
        p = PluginSpec(name="x")
        d = p.to_dict()
        assert d["name"] == "x"


class TestPluginRuntimeT044:
    def test_manifest_validation(self):
        from aios.plugin_runtime.manifest import PluginManifest
        assert PluginManifest(name="", version="").validate()
        assert PluginManifest(plugin_id="p1", name="plug", version="1.0.0").validate() == []

    def test_resolver_dependency_order(self):
        from aios.plugin_runtime.manifest import PluginManifest
        from aios.plugin_runtime.resolver import PluginResolver
        a = PluginManifest(plugin_id="a", name="a", dependencies=["b"])
        b = PluginManifest(plugin_id="b", name="b")
        order = PluginResolver().resolve(a, {"a": a, "b": b})
        assert order.index("b") < order.index("a")

    def test_runtime_manifest_register_and_rollback(self):
        rt = PluginRuntime()
        m = PluginManifest(plugin_id="p1", name="plug", version="1.0.0")
        spec = rt.register_manifest(m)
        rt.load(spec.plugin_id)
        rt.enable(spec.plugin_id)
        assert rt.get_plugin("p1").state == PluginState.ENABLED
        rt.rollback("p1")
        assert rt.get_plugin("p1").state == PluginState.REGISTERED

    def test_runtime_rejects_invalid_manifest(self):
        rt = PluginRuntime()
        try:
            rt.register_manifest(PluginManifest(plugin_id="", name=""))
            assert False, "should raise"
        except ValueError:
            pass
