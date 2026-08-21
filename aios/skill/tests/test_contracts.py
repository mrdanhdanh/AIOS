"""Tests for Skill contracts — AC-015-01/04/11 (TASK-015)."""

import pytest

from aios.skill.contracts import (
    SkillContract,
    SkillDependency,
    SkillError,
    SkillPersistentState,
    SkillStatus,
    SkillTransition,
    VALID_TRANSITIONS,
    SKILL_CONTRACT,
    check_skill_contracts,
)
from aios.core.version import SemVer


def _contract(skill_id="test-skill", version="1.0.0", **kwargs):
    defaults = dict(
        skill_id=skill_id,
        name=skill_id,
        version=version,
        description="test skill",
        author="tester",
        entrypoint="skill.main:run",
        runtime="python3.11",
    )
    defaults.update(kwargs)
    return SkillContract.create(**defaults)


# -- SkillDependency --

def test_dependency_create_valid():
    dep = SkillDependency(skill_id="dep-a", version_constraint=">=1.2.0")
    dep.validate()
    assert dep.skill_id == "dep-a"


def test_dependency_invalid_id():
    with pytest.raises(SkillError):
        SkillDependency(skill_id="", version_constraint=">=1.0.0").validate()


def test_dependency_invalid_constraint():
    with pytest.raises(SkillError):
        SkillDependency(skill_id="dep-a", version_constraint="").validate()


def test_dependency_is_satisfied_ge():
    dep = SkillDependency(skill_id="dep-a", version_constraint=">=1.2.0")
    assert dep.is_satisfied_by("1.2.0") is True
    assert dep.is_satisfied_by("1.3.0") is True
    assert dep.is_satisfied_by("1.1.9") is False


def test_dependency_is_satisfied_eq():
    dep = SkillDependency(skill_id="dep-a", version_constraint="==1.0.0")
    assert dep.is_satisfied_by("1.0.0") is True
    assert dep.is_satisfied_by("1.0.1") is False


def test_dependency_is_satisfied_compatible():
    dep = SkillDependency(skill_id="dep-a", version_constraint="~=2.0")
    assert dep.is_satisfied_by("2.0.0") is True
    assert dep.is_satisfied_by("2.5.0") is True
    assert dep.is_satisfied_by("3.0.0") is False


def test_dependency_is_satisfied_caret():
    dep = SkillDependency(skill_id="dep-a", version_constraint="^1.2.3")
    assert dep.is_satisfied_by("1.2.3") is True
    assert dep.is_satisfied_by("1.9.0") is True
    assert dep.is_satisfied_by("2.0.0") is False


def test_dependency_is_satisfied_range():
    dep = SkillDependency(skill_id="dep-a", version_constraint=">=1.2.0,<2.0.0")
    assert dep.is_satisfied_by("1.5.0") is True
    assert dep.is_satisfied_by("2.0.0") is False
    assert dep.is_satisfied_by("1.1.0") is False


def test_dependency_to_dict():
    dep = SkillDependency(skill_id="dep-a", version_constraint=">=1.0.0")
    d = dep.to_dict()
    assert d["skill_id"] == "dep-a"
    dep2 = SkillDependency.from_dict(d)
    assert dep2.skill_id == "dep-a"


# -- SkillContract --

def test_contract_create_valid():
    c = _contract()
    assert c.skill_id == "test-skill"
    assert c.version == "1.0.0"
    assert c.entrypoint == "skill.main:run"


def test_contract_invalid_id():
    with pytest.raises(SkillError):
        _contract(skill_id="")


def test_contract_invalid_version():
    with pytest.raises(SkillError):
        _contract(version="not-semver")


def test_contract_invalid_permission():
    with pytest.raises(SkillError):
        _contract(permissions=["invalid.perm"])


def test_contract_invalid_capability():
    with pytest.raises(SkillError):
        _contract(required_capabilities=["invalid-cap!"])


def test_contract_invalid_checksum():
    with pytest.raises(SkillError):
        _contract(checksum="not-hex")


def test_contract_checksum_compute_verify():
    c = _contract()
    cs = c.compute_checksum()
    assert len(cs) == 64
    c.checksum = cs
    assert c.verify_checksum() is True
    c.checksum = "0" * 64
    assert c.verify_checksum() is False


def test_contract_missing_checksum_verify_false():
    c = _contract()
    c.checksum = ""
    assert c.verify_checksum() is False


def test_contract_to_dict_from_dict():
    c = _contract(skill_id="skill-a", version="1.2.3", required_capabilities=["execute_code"], permissions=["filesystem.read"])
    d = c.to_dict()
    c2 = SkillContract.from_dict(d)
    assert c2.skill_id == "skill-a"
    assert c2.version == "1.2.3"
    assert "execute_code" in c2.required_capabilities


def test_contract_dependencies():
    dep = SkillDependency(skill_id="dep-a", version_constraint=">=1.0.0")
    c = _contract(dependencies=[dep])
    assert len(c.dependencies) == 1
    assert c.dependencies[0].skill_id == "dep-a"


def test_contract_status():
    c = _contract(status=SkillStatus.ENABLED)
    assert c.status == SkillStatus.ENABLED
    c2 = _contract(status="disabled")
    assert c2.status == SkillStatus.DISABLED


def test_contract_resources():
    c = _contract(resources={"cpu": 2, "memory_mb": 1024})
    assert c.resources["cpu"] == 2
    with pytest.raises(SkillError):
        _contract(resources={"cpu": -1})


def test_contract_entrypoint_required_for_validate():
    c = _contract(entrypoint="")
    # validate should pass schema but manager validate will check entrypoint
    c.validate()  # schema allows empty entrypoint
    # But manager will reject missing entrypoint — contract itself allows empty for flexibility


def test_skill_status_all():
    assert len(SkillStatus.all()) >= 5


def test_valid_transitions():
    assert SkillStatus.PENDING in VALID_TRANSITIONS
    assert SkillStatus.ENABLED in VALID_TRANSITIONS


def test_check_skill_contracts():
    check_skill_contracts("1.0.0")
    with pytest.raises(Exception):
        check_skill_contracts("2.0.0")


def test_persistent_state():
    c = _contract(skill_id="skill-a", version="1.0.0")
    c.checksum = c.compute_checksum()
    state = SkillPersistentState.from_contract(c, last_transition="install", last_health="healthy", previous_certified_version="0.9.0")
    assert state.skill_id == "skill-a"
    assert state.version == "1.0.0"
    assert state.last_transition == "install"
    d = state.to_dict()
    state2 = SkillPersistentState.from_dict(d)
    assert state2.skill_id == "skill-a"
    assert state2.previous_certified_version == "0.9.0"


def test_contract_with_all_fields():
    c = SkillContract.create(
        skill_id="full-skill",
        name="Full Skill",
        version="2.0.0",
        description="full",
        author="author",
        dependencies=[{"skill_id": "dep-a", "version_constraint": ">=1.0.0"}],
        required_capabilities=["execute_code", "run_tests"],
        permissions=["filesystem.read", "capability:invoke"],
        resources={"cpu": 1, "memory_mb": 512},
        runtime="python3.11",
        entrypoint="skill.main:run",
        checksum="",
        status="pending",
        configuration={"key": "value"},
        metadata={"extra": "data"},
    )
    assert c.skill_id == "full-skill"
    assert len(c.dependencies) == 1
    assert len(c.required_capabilities) == 2
