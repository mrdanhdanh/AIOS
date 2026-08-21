"""Tests for plugin runtime."""
from __future__ import annotations
import pytest
from aios.plugin_runtime.contracts import PluginSpec, PluginState
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
