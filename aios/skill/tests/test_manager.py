"""Tests for Skill Manager lifecycle — AC-015-01/02/06/09/10/11/12 (TASK-015)."""

import pytest

from aios.skill.contracts import SkillContract, SkillDependency, SkillStatus
from aios.skill.registry import SkillRegistry
from aios.skill.resolver import SkillDependencyResolver
from aios.skill.sandbox import SandboxPool
from aios.skill.manager import SkillManager, SkillManagerError


def _contract(skill_id="skill-a", version="1.0.0", deps=None, caps=None, **kwargs):
    deps_list = []
    for d in deps or []:
        if isinstance(d, str):
            deps_list.append(SkillDependency(skill_id=d, version_constraint=">=1.0.0"))
        elif isinstance(d, dict):
            deps_list.append(SkillDependency.from_dict(d))
        else:
            deps_list.append(d)
    return SkillContract.create(
        skill_id=skill_id,
        version=version,
        entrypoint="skill.main:run",
        dependencies=deps_list,
        required_capabilities=caps or [],
        **kwargs,
    )


def _manager(**kwargs):
    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=5)
    return SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool, **kwargs), reg, pool


# -- Install --

def test_install_valid():
    mgr, reg, _ = _manager()
    c = _contract("skill-a")
    installed = mgr.install(c)
    assert installed.skill_id == "skill-a"
    assert reg.get_status("skill-a") == SkillStatus.INSTALLED
    assert installed.checksum != ""


def test_install_duplicate_reject():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    with pytest.raises(SkillManagerError):
        mgr.install(_contract("skill-a"))


def test_install_checksum_mismatch():
    mgr, _, _ = _manager()
    c = _contract("skill-a")
    c.checksum = "0" * 64
    with pytest.raises(SkillManagerError, match="Checksum"):
        mgr.install(c)


def test_install_policy_deny():
    class DenyPolicy:
        def evaluate(self, req):
            class R:
                class D:
                    value = "deny"
                decision = D()
            return R()
    mgr, _, _ = _manager(policy_engine=DenyPolicy())
    with pytest.raises(SkillManagerError, match="Policy"):
        mgr.install(_contract("skill-a"))


# -- Enable / Disable --

def test_enable_valid():
    mgr, reg, _ = _manager()
    mgr.install(_contract("skill-a"))
    enabled = mgr.enable("skill-a")
    assert enabled.status == SkillStatus.ENABLED
    assert reg.is_enabled("skill-a") is True


def test_enable_invalid_transition():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    # Already ENABLED — cannot enable again via same path (but upgrade allows)
    with pytest.raises(SkillManagerError):
        mgr.enable("skill-a")


def test_enable_missing_dependency():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", deps=["skill-b"]))
    with pytest.raises(SkillManagerError, match="Dependency"):
        mgr.enable("skill-a")


def test_enable_with_dependency():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-b"))
    mgr.install(_contract("skill-a", deps=["skill-b"]))
    mgr.enable("skill-b")
    enabled = mgr.enable("skill-a")
    assert enabled.status == SkillStatus.ENABLED


def test_enable_cycle_fail():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", deps=["skill-b"]))
    mgr.install(_contract("skill-b", deps=["skill-a"]))
    with pytest.raises(SkillManagerError, match="Circular"):
        mgr.enable("skill-a")


def test_disable_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    disabled = mgr.disable("skill-a")
    assert disabled.status == SkillStatus.DISABLED


def test_disable_not_enabled():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    with pytest.raises(SkillManagerError):
        mgr.disable("skill-a")


def test_disable_enable_cycle():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    mgr.disable("skill-a")
    mgr.enable("skill-a")
    assert mgr._registry.get_status("skill-a") == SkillStatus.ENABLED


# -- Unload / Reload --

def test_unload_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    unloaded = mgr.unload("skill-a")
    assert unloaded.status == SkillStatus.UNLOADED


def test_unload_not_allowed():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    with pytest.raises(SkillManagerError):
        mgr.unload("skill-a")


def test_reload_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    mgr.unload("skill-a")
    reloaded = mgr.reload("skill-a")
    assert reloaded.status == SkillStatus.ENABLED


def test_reload_invalid_status():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    with pytest.raises(SkillManagerError):
        mgr.reload("skill-a")


def test_reload_idempotent():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    mgr.disable("skill-a")
    # DISABLED -> RELOAD should work
    reloaded = mgr.reload("skill-a")
    assert reloaded.status == SkillStatus.ENABLED


# -- Validate --

def test_validate_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    assert mgr.validate("skill-a") is True


def test_validate_missing_entrypoint():
    mgr, _, _ = _manager()
    c = SkillContract.create(skill_id="skill-a", version="1.0.0", entrypoint="", required_capabilities=[])
    # Bypass install validation by directly registering
    mgr._registry.register(c)
    mgr._registry.set_status("skill-a", SkillStatus.INSTALLED)
    with pytest.raises(SkillManagerError, match="entrypoint"):
        mgr.validate("skill-a")


def test_validate_checksum_required():
    mgr, _, _ = _manager()
    c = _contract("skill-a")
    c.checksum = ""
    mgr._registry.register(c)
    mgr._registry.set_status("skill-a", SkillStatus.INSTALLED)
    with pytest.raises(SkillManagerError, match="checksum"):
        mgr.validate(c, require_checksum=True)


def test_validate_checksum_mismatch():
    mgr, _, _ = _manager()
    c = _contract("skill-a")
    c.checksum = "0" * 64
    mgr._registry.register(c)
    mgr._registry.set_status("skill-a", SkillStatus.INSTALLED)
    with pytest.raises(SkillManagerError, match="Checksum"):
        mgr.validate(c)


# -- Upgrade --

def test_upgrade_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    new_c = _contract("skill-a", version="2.0.0")
    upgraded = mgr.upgrade("skill-a", new_c)
    assert upgraded.version == "2.0.0"
    assert upgraded.status == SkillStatus.ENABLED


def test_upgrade_preserves_certified_on_failure():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    # New contract with invalid dependency (missing)
    new_c = _contract("skill-a", version="2.0.0", deps=["missing-skill"])
    with pytest.raises(SkillManagerError):
        mgr.upgrade("skill-a", new_c)
    # Certified should still be 1.0.0
    assert mgr._registry.get("skill-a").version == "1.0.0"


def test_upgrade_wrong_id():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    new_c = _contract("skill-b", version="2.0.0")
    with pytest.raises(SkillManagerError):
        mgr.upgrade("skill-a", new_c)


# -- Rollback --

def test_rollback_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    new_c = _contract("skill-a", version="2.0.0")
    mgr.upgrade("skill-a", new_c)
    assert mgr._registry.get("skill-a").version == "2.0.0"
    rolled = mgr.rollback("skill-a")
    assert rolled.version == "1.0.0"


def test_rollback_no_certified():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    with pytest.raises(SkillManagerError, match="certified"):
        mgr.rollback("skill-a")


def test_rollback_already_certified():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    # No upgrade, so already at certified
    with pytest.raises(SkillManagerError, match="Already at certified"):
        mgr.rollback("skill-a")


# -- Remove --

def test_remove_valid():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.disable("skill-a") if mgr._registry.get_status("skill-a") == SkillStatus.ENABLED else None
    # Need to enable then disable to get to DISABLED
    # Actually install -> INSTALLED, need to enable then disable
    mgr2, _, _ = _manager()
    mgr2.install(_contract("skill-a"))
    mgr2.enable("skill-a")
    mgr2.disable("skill-a")
    mgr2.remove("skill-a")
    assert "skill-a" not in mgr2._registry


def test_remove_with_dependency():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-b"))
    mgr.install(_contract("skill-a", deps=["skill-b"]))
    mgr.enable("skill-b")
    mgr.enable("skill-a")
    mgr.disable("skill-b") if mgr._registry.get_status("skill-b") == SkillStatus.ENABLED else None
    # skill-b is required by skill-a, cannot remove
    # First disable skill-b
    # But skill-a still depends on it
    # Try to remove skill-b — should fail
    # Need to get skill-b to DISABLED
    if mgr._registry.get_status("skill-b") == SkillStatus.ENABLED:
        mgr.disable("skill-b")
    with pytest.raises(SkillManagerError, match="still required"):
        mgr.remove("skill-b")


def test_remove_invalid_status():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    with pytest.raises(SkillManagerError):
        mgr.remove("skill-a")


def test_remove_with_active_execution():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    mgr.disable("skill-a")
    mgr._active_executions["skill-a"] = 1
    with pytest.raises(SkillManagerError, match="active"):
        mgr.remove("skill-a")


# -- Execute --

def test_execute_success():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    result = mgr.execute("skill-a", payload={"data": "test"})
    assert result.status == "completed"
    assert result.skill_id == "skill-a"
    assert result.sandbox_id is not None


def test_execute_not_enabled():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    with pytest.raises(SkillManagerError):
        mgr.execute("skill-a", payload="test")


def test_execute_policy_blocked():
    class DenyPolicy:
        def evaluate(self, req):
            # Deny execute but allow other actions
            if req.action == "skill.execute":
                class R:
                    class D:
                        value = "deny"
                    decision = D()
                return R()
            class R2:
                class D2:
                    value = "allow"
                decision = D2()
            return R2()
    mgr, _, _ = _manager(policy_engine=DenyPolicy())
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    result = mgr.execute("skill-a", payload="test")
    assert result.status == "blocked"


def test_execute_unknown_skill():
    mgr, _, _ = _manager()
    with pytest.raises(SkillManagerError):
        mgr.execute("unknown", payload="test")


# -- Resolve --

def test_resolve_success():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-b"))
    mgr.install(_contract("skill-a", deps=["skill-b"]))
    result = mgr.resolve("skill-a")
    assert result.is_success


def test_resolve_cycle():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a", deps=["skill-b"]))
    mgr.install(_contract("skill-b", deps=["skill-a"]))
    with pytest.raises(SkillManagerError, match="Circular"):
        mgr.resolve("skill-a")


# -- Health check --

def test_health_check():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    assert mgr.health_check("skill-a") is True
    assert mgr.health_check("unknown") is False


# -- Evidence --

def test_evidence_recorded():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    history = mgr.get_history("skill-a")
    assert len(history) >= 2
    evidence = mgr.list_evidence()
    assert len(evidence) >= 2
    # Check evidence has required fields
    for rec in evidence:
        assert rec.evidence_id.startswith("ev-")
        assert rec.skill_id == "skill-a"


def test_transition_invalid_reject():
    mgr, _, _ = _manager()
    mgr.install(_contract("skill-a"))
    # Try to disable when not enabled
    with pytest.raises(SkillManagerError):
        mgr.disable("skill-a")
    # Try to unload when not enabled/disabled
    with pytest.raises(SkillManagerError):
        mgr.unload("skill-a")


# -- Offline-first --

def test_offline_lifecycle():
    """AC-015-11: lifecycle works without LLM/network."""
    mgr, _, _ = _manager()
    # No policy, no capability registry, no network — should still work
    c = _contract("skill-a")
    mgr.install(c)
    mgr.enable("skill-a")
    result = mgr.execute("skill-a", payload="offline test")
    assert result.status == "completed"
    mgr.disable("skill-a")
    mgr.unload("skill-a")
    mgr.reload("skill-a")
    assert mgr._registry.get_status("skill-a") == SkillStatus.ENABLED
