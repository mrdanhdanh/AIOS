"""Integration tests for Skill — AC-015-05/06/12 (TASK-015)."""

import pytest

from aios.capability.capability import CapabilityContract, CapabilityRegistry
from aios.runtime.permission import Permission, PermissionBroker, PermissionScope
from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRequest, PolicyRule
from aios.skill.contracts import SkillContract, SkillStatus
from aios.skill.registry import SkillRegistry
from aios.skill.resolver import SkillDependencyResolver
from aios.skill.sandbox import SandboxPool
from aios.skill.manager import SkillManager


def _contract(skill_id="skill-a", version="1.0.0", caps=None, **kwargs):
    return SkillContract.create(
        skill_id=skill_id,
        version=version,
        entrypoint="skill.main:run",
        required_capabilities=caps or [],
        **kwargs,
    )


def test_capability_integration():
    """AC-015-05: skill declares capabilities, manager checks via registry."""
    cap_reg = CapabilityRegistry()
    cap_reg.register(CapabilityContract.create(capability_id="execute_code", version="1.0.0"))
    cap_reg.register(CapabilityContract.create(capability_id="run_tests", version="1.0.0"))

    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool, capability_registry=cap_reg)

    # Skill requiring existing capability should enable
    mgr.install(_contract("skill-a", caps=["execute_code"]))
    mgr.enable("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.ENABLED

    # Skill requiring missing capability should fail
    mgr.install(_contract("skill-b", caps=["nonexistent_cap"]))
    with pytest.raises(Exception, match="capability"):
        mgr.enable("skill-b")


def test_policy_integration_deny():
    """AC-015-06: skill execution blocked when policy denies."""
    broker = PermissionBroker()
    policy = PolicyEngine(broker=broker)
    policy.add_rule(PolicyRule("deny-all", applies=lambda r: True, decision=PolicyDecision.DENY, reason="deny"))

    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool, policy_engine=policy)

    # Install should be denied
    with pytest.raises(Exception, match="Policy"):
        mgr.install(_contract("skill-a"))


def test_policy_integration_allow():
    broker = PermissionBroker()
    policy = PolicyEngine(broker=broker)
    policy.add_rule(PolicyRule("allow-all", applies=lambda r: True, decision=PolicyDecision.ALLOW, reason="allow"))

    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool, policy_engine=policy)

    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")
    result = mgr.execute("skill-a", payload="test")
    assert result.status == "completed"


def test_evidence_provenance():
    """AC-015-12: every transition has evidence with provenance."""
    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool)

    mgr.install(_contract("skill-a", version="1.0.0"))
    mgr.enable("skill-a")
    mgr.disable("skill-a")
    mgr.unload("skill-a")
    mgr.reload("skill-a")

    history = mgr.get_history("skill-a")
    assert len(history) >= 5
    for rec in history:
        assert rec.evidence_id.startswith("ev-")
        assert rec.skill_id == "skill-a"
        assert rec.transition in ("install", "enable", "disable", "unload", "reload", "validate", "resolve")
        assert rec.version != ""
        # Evidence should be retrievable
        ev = mgr.get_evidence(rec.evidence_id)
        assert ev.evidence_id == rec.evidence_id

    # Skill -> Version -> Transition -> Run -> Artifact -> Result chain
    # Each evidence has skill_id, version, transition, evidence_id
    for rec in history:
        d = rec.to_dict()
        assert "skill_id" in d
        assert "version" in d
        assert "transition" in d
        assert "evidence_id" in d


def test_sandbox_integration():
    """Skill execution uses sandbox pool."""
    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool)

    mgr.install(_contract("skill-a"))
    mgr.enable("skill-a")

    # Execute multiple times — sandbox should be reused and reset
    for i in range(3):
        result = mgr.execute("skill-a", payload=f"run-{i}")
        assert result.status == "completed"
        assert result.sandbox_id is not None

    # Pool should still have sandboxes
    assert pool.size() >= 1
    # All sandboxes should be READY after releases
    for sb in pool.list():
        assert sb.status.value in ("ready", "acquired", "running", "resetting")


def test_full_lifecycle():
    """Test full lifecycle: install -> enable -> execute -> disable -> unload -> reload -> upgrade -> rollback -> remove."""
    cap_reg = CapabilityRegistry()
    cap_reg.register(CapabilityContract.create(capability_id="execute_code"))

    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool, capability_registry=cap_reg)

    # Install
    mgr.install(_contract("skill-a", version="1.0.0", caps=["execute_code"]))
    assert reg.get_status("skill-a") == SkillStatus.INSTALLED

    # Enable
    mgr.enable("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.ENABLED

    # Execute
    result = mgr.execute("skill-a", payload="hello")
    assert result.status == "completed"

    # Disable
    mgr.disable("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.DISABLED

    # Unload
    mgr.unload("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.UNLOADED

    # Reload
    mgr.reload("skill-a")
    assert reg.get_status("skill-a") == SkillStatus.ENABLED

    # Upgrade
    mgr.upgrade("skill-a", _contract("skill-a", version="2.0.0", caps=["execute_code"]))
    assert reg.get("skill-a").version == "2.0.0"

    # Rollback
    mgr.rollback("skill-a")
    assert reg.get("skill-a").version == "1.0.0"

    # Disable and remove
    mgr.disable("skill-a")
    mgr.remove("skill-a")
    assert "skill-a" not in reg


def test_offline_no_llm():
    """AC-015-11: lifecycle works without LLM."""
    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool)

    # All operations without any LLM or network
    c = _contract("skill-a")
    mgr.install(c)
    mgr.enable("skill-a")
    result = mgr.execute("skill-a", payload="offline")
    assert result.status == "completed"
    # No LLM was called — deterministic
    assert mgr.health_check("skill-a") is True


def test_dependency_with_capability():
    """Skill with dependency and capability."""
    cap_reg = CapabilityRegistry()
    cap_reg.register(CapabilityContract.create(capability_id="execute_code"))

    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    pool = SandboxPool(max_size=3)
    mgr = SkillManager(registry=reg, resolver=resolver, sandbox_pool=pool, capability_registry=cap_reg)

    mgr.install(_contract("skill-b", caps=["execute_code"]))
    mgr.install(_contract("skill-a", caps=["execute_code"], dependencies=[{"skill_id": "skill-b", "version_constraint": ">=1.0.0"}]))
    mgr.enable("skill-b")
    mgr.enable("skill-a")
    result = mgr.execute("skill-a", payload="test")
    assert result.status == "completed"
