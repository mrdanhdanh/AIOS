"""Tests for ControlCenterAggregator (TASK-237, M34)."""
from __future__ import annotations

from aios.dashboard.control_center import (
    ControlCenterAggregator,
    ControlCenterView,
    PlaneSnapshot,
)


def test_aggregator_returns_all_14_planes():
    agg = ControlCenterAggregator()
    snap = agg.snapshot(system_health="healthy")
    assert isinstance(snap, ControlCenterView)
    assert snap.system_health == "healthy"
    assert snap.plane_count == 14
    for name in ControlCenterAggregator.PLANES:
        assert name in snap.planes
        assert snap.planes[name].status == "empty"


def test_aggregator_collects_ok_plane():
    agg = ControlCenterAggregator(collectors={"goals": lambda: {"active": 3}})
    snap = agg.snapshot()
    assert snap.planes["goals"].status == "ok"
    assert snap.planes["goals"].data == {"active": 3}


def test_aggregator_isolates_plane_errors():
    def boom() -> dict:
        raise RuntimeError("subsystem down")

    agg = ControlCenterAggregator(collectors={"agents": boom})
    snap = agg.snapshot()
    # Failing plane -> error entry, others still collected.
    assert snap.planes["agents"].status == "error"
    assert "subsystem down" in snap.planes["agents"].error
    assert snap.planes["executions"].status == "empty"
    assert snap.plane_count == 14


def test_aggregator_deterministic():
    agg = ControlCenterAggregator(collectors={"coding": lambda: {"files": 5}})
    a = agg.snapshot()
    b = agg.snapshot()
    assert a.to_dict() == b.to_dict()
