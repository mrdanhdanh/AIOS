"""Tests for Asset Pipeline + Capability Registry + Routing (TASK-081, M11)."""

from __future__ import annotations

import pytest

from aios.asset_pipeline.pipeline import (
    AssetRecord,
    AssetRegistry,
    AssetCapabilityRegistry,
    AssetRouter,
    AssetValidator,
    AssetError,
    sha256,
)


def _asset(asset_type="image", content="data", caps=("cap.img",)):
    h = sha256(content)
    return AssetRecord(
        asset_id="a1", asset_type=asset_type, version="1.0.0", content_hash=h,
        capable_capabilities=list(caps), evidence_ref="ev-1",
    ), content


def test_registry_stores_and_looks_up():
    reg = AssetRegistry()
    asset, _ = _asset()
    reg.register(asset)
    assert reg.get("a1", "1.0.0") is asset
    assert reg.latest("a1") is asset


def test_capability_registry_maps_type():
    caps = AssetCapabilityRegistry()
    caps.register_capability("image", "cap.img")
    caps.register_capability("image", "cap.vision")
    assert set(caps.capable_capabilities("image")) == {"cap.img", "cap.vision"}
    assert caps.has_capability("image") is True
    assert caps.has_capability("audio") is False


def test_route_valid_asset_to_capability():
    caps = AssetCapabilityRegistry()
    caps.register_capability("image", "cap.img")
    router = AssetRouter(caps)
    asset, content = _asset()
    assert router.route(asset, content) == "cap.img"


def test_route_invalid_asset_fails_closed():
    caps = AssetCapabilityRegistry()
    caps.register_capability("image", "cap.img")
    router = AssetRouter(caps)
    asset, content = _asset()
    asset.content_hash = "wrong"  # tampered
    with pytest.raises(AssetError):
        router.route(asset, content)


def test_route_unregistered_type_fails_closed():
    caps = AssetCapabilityRegistry()
    router = AssetRouter(caps)
    asset, content = _asset(asset_type="video")
    with pytest.raises(AssetError):
        router.route(asset, content)


def test_validator_schema_required_fields():
    v = AssetValidator()
    asset, content = _asset()
    asset.schema = {"required_fields": ["w"], "fields": {"w": 1}}
    assert v.validate(asset, content) is True
    asset.schema = {"required_fields": ["missing"], "fields": {}}
    assert v.validate(asset, content) is False


def test_deterministic_routing_same_type():
    caps = AssetCapabilityRegistry()
    caps.register_capability("image", "cap.img")
    router = AssetRouter(caps)
    a1, c1 = _asset()
    a2, c2 = _asset()
    assert router.route(a1, c1) == router.route(a2, c2)
