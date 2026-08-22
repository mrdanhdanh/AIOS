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


class TestExtensionContractsT045:
    def test_extension_context(self):
        from aios.extension_contracts.contracts import ExtensionContext
        ctx = ExtensionContext(tenant_id="t1", scope="public")
        assert ctx.to_dict()["scope"] == "public"

    def test_compatibility(self):
        from aios.extension_contracts.compatibility import is_compatible
        assert is_compatible("1.2.0", "1.0.0") is True
        assert is_compatible("2.0.0", "1.0.0") is False

    def test_dependency_resolver(self):
        from aios.extension_contracts.compatibility import ExtensionDependencyResolver
        a = ExtensionSpec(spec_id="a", name="a", version="1.0.0")
        a.dependencies = ["b"]  # type: ignore[attr-defined]
        b = ExtensionSpec(spec_id="b", name="b", version="1.0.0")
        order = ExtensionDependencyResolver().resolve(a, {"a": a, "b": b})
        assert order.index("b") < order.index("a")

    def test_boundary_rejects_internal_imports(self):
        v = ExtensionValidator()
        res = v.check_boundary(ExtensionSpec(name="x"), ["aios.runtime.kernel", "aios.public_api"])
        assert res["valid"] is False
        assert "aios.runtime.kernel" in res["violations"]

    def test_error_and_evidence(self):
        from aios.extension_contracts.evidence import make_error, make_evidence
        err = make_error("E1", "bad", "ext-1")
        assert err.code == "E1"
        ev = make_evidence("ext-1", "load", ["src:manifest"])
        assert ev.extension_id == "ext-1"
