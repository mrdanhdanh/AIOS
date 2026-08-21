"""Tests for Skill persistence — AC-015-03 (TASK-015)."""

import pytest

from aios.skill.contracts import SkillContract, SkillStatus
from aios.skill.registry import SkillRegistry
from aios.skill.resolver import SkillDependencyResolver
from aios.skill.sandbox import SandboxPool
from aios.skill.manager import SkillManager


def _contract(skill_id="skill-a", version="1.0.0", **kwargs):
    return SkillContract.create(
        skill_id=skill_id,
        version=version,
        entrypoint="skill.main:run",
        **kwargs,
    )


def _manager():
    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=5)
    return SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool), reg


def test_persist_and_restore():
    mgr, reg = _manager()
    mgr.install(_contract("skill-a", version="1.4.0"))
    mgr.enable("skill-a")
    # Persist
    snapshot = mgr.persist()
    assert "skill-a" in snapshot["registry"]
    assert snapshot["registry"]["skill-a"]["version"] == "1.4.0"
    assert snapshot["registry"]["skill-a"]["status"] == "enabled"
    # Simulate restart: create new manager and restore
    mgr2, reg2 = _manager()
    mgr2.restore(snapshot)
    assert "skill-a" in mgr2._registry
    assert mgr2._registry.get("skill-a").version == "1.4.0"
    assert mgr2._registry.get_status("skill-a") == SkillStatus.ENABLED
    # Persistent state should be restored
    state = mgr2.get_persistent_state("skill-a")
    assert state.version == "1.4.0"
    assert state.enabled is True


def test_persist_disabled():
    mgr, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    mgr.disable("skill-a")
    snapshot = mgr.persist()
    mgr2, _ = _manager()
    mgr2.restore(snapshot)
    assert mgr2._registry.get_status("skill-a") == SkillStatus.DISABLED
    # Must not default to ENABLED
    assert mgr2._registry.get_status("skill-a") != SkillStatus.ENABLED


def test_persist_multiple_skills():
    mgr, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.install(_contract("skill-b", version="2.0.0"))
    mgr.enable("skill-a")
    # skill-b stays INSTALLED
    snapshot = mgr.persist()
    mgr2, _ = _manager()
    mgr2.restore(snapshot)
    assert mgr2._registry.get_status("skill-a") == SkillStatus.ENABLED
    assert mgr2._registry.get_status("skill-b") == SkillStatus.INSTALLED


def test_persist_upgrade_version():
    mgr, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    new_c = _contract("skill-a", version="1.4.0")
    mgr.upgrade("skill-a", new_c)
    snapshot = mgr.persist()
    mgr2, _ = _manager()
    mgr2.restore(snapshot)
    assert mgr2._registry.get("skill-a").version == "1.4.0"
    assert mgr2._registry.get_status("skill-a") == SkillStatus.ENABLED
    # Previous version should be tracked
    assert mgr2._previous_version.get("skill-a") == "1.0.0"


def test_persist_list_states():
    mgr, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    states = mgr.list_persistent_states()
    assert len(states) == 1
    assert states[0].skill_id == "skill-a"


def test_persist_get_unknown():
    mgr, _ = _manager()
    with pytest.raises(Exception):
        mgr.get_persistent_state("unknown")


def test_restore_empty():
    mgr, _ = _manager()
    mgr.restore({"registry": {}, "persistent": {}, "certified": {}, "previous_version": {}})
    assert len(mgr._registry) == 0


def test_persist_after_rollback():
    mgr, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    new_c = _contract("skill-a", version="2.0.0")
    mgr.upgrade("skill-a", new_c)
    mgr.rollback("skill-a")
    snapshot = mgr.persist()
    mgr2, _ = _manager()
    mgr2.restore(snapshot)
    assert mgr2._registry.get("skill-a").version == "1.0.0"
