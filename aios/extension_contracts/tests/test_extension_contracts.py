"""Tests for extension contracts."""
from __future__ import annotations
from aios.extension_contracts.contracts import CapabilityExport, ExtensionManifest, ExtensionSpec
from aios.extension_contracts.validator import ExtensionValidator

class TestExtensionContracts:
    def test_validate_spec_valid(self):
        v = ExtensionValidator()
        result = v.validate_spec(ExtensionSpec(name="test", version="1.0"))
        assert result["valid"]
    def test_validate_spec_no_name(self):
        v = ExtensionValidator()
        result = v.validate_spec(ExtensionSpec(name="", version="1.0"))
        assert not result["valid"]
    def test_validate_capability(self):
        v = ExtensionValidator()
        result = v.validate_capability(CapabilityExport(name="cap1"))
        assert result["valid"]
    def test_manifest(self):
        m = ExtensionManifest(author="test")
        assert m.to_dict()["author"] == "test"
    def test_extension_spec(self):
        s = ExtensionSpec(name="ext", version="2.0")
        d = s.to_dict()
        assert d["name"] == "ext"
