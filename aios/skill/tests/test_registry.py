"""Tests for Skill Registry — AC-015-01/04 (TASK-015)."""

import pytest

from aios.skill.contracts import SkillContract, SkillError, SkillStatus
from aios.skill.registry import SkillRegistry


def _contract(skill_id="skill-a", version="1.0.0", caps=None, **kwargs):
    return SkillContract.create(
        skill_id=skill_id,
        version=version,
        entrypoint="skill.main:run",
        required_capabilities=caps or [],
        **kwargs,
    )


def test_register_and_get():
    reg = SkillRegistry()
    c = _contract("skill-a")
    reg.register(c)
    assert reg.get("skill-a").skill_id == "skill-a"
    assert len(reg) == 1


def test_register_duplicate_reject():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    with pytest.raises(SkillError):
        reg.register(_contract("skill-a"))


def test_unregister():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    reg.unregister("skill-a")
    assert len(reg) == 0
    with pytest.raises(SkillError):
        reg.get("skill-a")


def test_unregister_unknown():
    reg = SkillRegistry()
    with pytest.raises(SkillError):
        reg.unregister("unknown")


def test_get_unknown():
    reg = SkillRegistry()
    with pytest.raises(SkillError):
        reg.get("unknown")


def test_list():
    reg = SkillRegistry()
    reg.register(_contract("skill-b"))
    reg.register(_contract("skill-a"))
    lst = reg.list()
    assert [c.skill_id for c in lst] == ["skill-a", "skill-b"]


def test_find():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", caps=["execute_code"]))
    reg.register(_contract("skill-b", caps=["run_tests"]))
    found = reg.find("execute_code")
    assert len(found) == 1
    assert found[0].skill_id == "skill-a"


def test_find_by_capability():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", caps=["execute_code"]))
    reg.register(_contract("skill-b", caps=["execute_code"]))
    reg.register(_contract("skill-c", caps=["run_tests"]))
    found = reg.find_by_capability("execute_code")
    assert len(found) == 2
    assert {c.skill_id for c in found} == {"skill-a", "skill-b"}


def test_capabilities_index():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", caps=["execute_code", "run_tests"]))
    caps = reg.capabilities()
    assert "execute_code" in caps
    assert "run_tests" in caps
    mapping = reg.list_capabilities()
    assert "skill-a" in mapping["execute_code"]


def test_status_tracking():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    assert reg.get_status("skill-a") == SkillStatus.PENDING
    reg.set_status("skill-a", SkillStatus.ENABLED)
    assert reg.get_status("skill-a") == SkillStatus.ENABLED
    assert reg.is_enabled("skill-a") is True
    reg.set_status("skill-a", SkillStatus.DISABLED)
    assert reg.is_enabled("skill-a") is False


def test_enable_disable():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    reg.enable("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.ENABLED
    reg.disable("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.DISABLED


def test_update():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", version="1.0.0"))
    c2 = _contract("skill-a", version="2.0.0")
    reg.update(c2)
    assert reg.get("skill-a").version == "2.0.0"


def test_update_unknown():
    reg = SkillRegistry()
    with pytest.raises(SkillError):
        reg.update(_contract("unknown"))


def test_contains():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    assert "skill-a" in reg
    assert "unknown" not in reg


def test_clear():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    reg.clear()
    assert len(reg) == 0


def test_capability_index_update_on_update():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", caps=["execute_code"]))
    c2 = _contract("skill-a", caps=["run_tests"])
    reg.update(c2)
    assert len(reg.find_by_capability("execute_code")) == 0
    assert len(reg.find_by_capability("run_tests")) == 1


def test_capability_index_remove_on_unregister():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", caps=["execute_code"]))
    reg.unregister("skill-a")
    assert len(reg.find_by_capability("execute_code")) == 0
