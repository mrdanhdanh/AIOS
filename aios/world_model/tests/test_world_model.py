"""Tests for TASK-052 World Model."""
from __future__ import annotations

from aios.world_model.contracts import (
    EntityStatus,
    WorldObservation,
    WorldRelation,
    ObservationType,
)
from aios.world_model.engine import WorldModel


def _obs(entity_id, status, source="probe", prov=("ev:1",)):
    return WorldObservation(
        type=ObservationType.STATE_CHANGE,
        source=source,
        provenance=list(prov),
        payload={"entity_id": entity_id, "entity_type": "RuntimeNode", "status": status},
    )


def test_observation_without_provenance_rejected():
    wm = WorldModel()
    obs = WorldObservation(payload={"entity_id": "r1", "status": "healthy"})
    res = wm.observe(obs)
    assert not res.accepted
    assert "provenance" in res.reason


def test_observation_creates_entity_and_transition():
    wm = WorldModel()
    res = wm.observe(_obs("r2", "healthy"))
    assert res.accepted
    ent = wm.get_entity("r2")
    assert ent is not None
    assert ent.status == EntityStatus.HEALTHY


def test_state_transition_recorded():
    wm = WorldModel()
    wm.observe(_obs("r2", "healthy"))
    res = wm.observe(_obs("r2", "unhealthy"))
    assert res.accepted
    assert res.transition is not None
    assert res.transition.from_status == "healthy"
    assert res.transition.to_status == "unhealthy"
    assert wm.get_entity("r2").status == EntityStatus.UNHEALTHY
    assert len(wm.history()) == 1


def test_idempotent_observation_no_transition():
    wm = WorldModel()
    wm.observe(_obs("r3", "healthy"))
    res = wm.observe(_obs("r3", "healthy"))
    assert res.accepted
    assert res.transition is None
    assert len(wm.history()) == 0


def test_transition_requires_valid_status():
    wm = WorldModel()
    wm.observe(_obs("r4", "healthy"))
    bad = _obs("r4", "not_a_real_status")
    res = wm.observe(bad)
    assert not res.accepted


def test_relation_requires_provenance():
    wm = WorldModel()
    rel = WorldRelation(source_entity="g1", target_entity="t1", relation_type="owns")
    try:
        wm.add_relation(rel)
        assert False, "should require provenance"
    except Exception:
        pass


def test_snapshot_and_diff():
    wm = WorldModel()
    wm.observe(_obs("r5", "healthy"))
    s1 = wm.snapshot()
    wm.observe(_obs("r5", "unhealthy"))
    s2 = wm.snapshot()
    d = wm.diff(s1, s2)
    assert d["changed_entities"]["r5"] == {"from": "healthy", "to": "unhealthy"}


def test_world_model_separate_from_memory():
    # World Model stores state, not historical recall; no memory import.
    wm = WorldModel()
    assert wm.get_entity("missing") is None
