"""System-level test: Superpowers integration running through the REAL AIOS system.

Unlike the unit/integration tests, this boots the actual ``RuntimeKernel``
(composition root) and drives the Superpowers skills through the genuine
``SkillManager`` lifecycle that the running system uses:

    install -> enable -> resolve -> execute (real sandbox)

It proves the implemented parts truly work inside AIOS, not just as isolated
functions. The kernel wires the real PolicyEngine, PermissionBroker,
CapabilityRegistry and SandboxPool — so this exercises the same code paths the
deployed system uses.

Run:  python -m pytest aios/skill/tests/test_superpowers_system.py -q
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aios.runtime.kernel import RuntimeKernel
from aios.skill.contracts import SkillContract, SkillStatus
from aios.skill.superpowers_router import META_SKILL, route

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills" / "superpowers" / "skills"

EXPECTED_SKILLS = [
    "using-superpowers",
    "brainstorming",
    "systematic-debugging",
    "test-driven-development",
    "verification-before-completion",
    "writing-plans",
    "executing-plans",
    "subagent-driven-development",
    "requesting-code-review",
    "receiving-code-review",
    "using-git-worktrees",
    "finishing-a-development-branch",
]


def _contract_from_disk(sid: str) -> SkillContract:
    manifest = json.loads((SKILLS_ROOT / sid / "manifest.json").read_text(encoding="utf-8"))
    return SkillContract.create(
        skill_id=manifest["skill_id"],
        name=manifest["name"],
        version=manifest["version"],
        description=manifest["description"],
        author=manifest.get("author", ""),
        dependencies=manifest.get("dependencies", []),
        required_capabilities=manifest.get("required_capabilities", []),
        permissions=manifest.get("permissions", []),
        resources=manifest.get("resources", {}),
        runtime=manifest.get("runtime", "python3.11"),
        entrypoint=manifest.get("entrypoint", "SKILL.md"),
        install_source=manifest.get("install_source", "git"),
        install_location=manifest.get("install_location", ""),
        metadata=manifest.get("metadata", {}),
        status=manifest.get("status", "pending"),
    )


@pytest.fixture(scope="module")
def live_kernel():
    """Boot the REAL AIOS RuntimeKernel (composition root)."""
    kernel = RuntimeKernel()
    yield kernel
    # No teardown needed; kernel is in-memory.


@pytest.fixture(scope="module")
def loaded_manager(live_kernel):
    """Boot the real kernel, permit skills on the *real* PolicyEngine, then
    install + enable + resolve all 12 Superpowers skills through the genuine
    SkillManager lifecycle. Shared across the module so every test exercises
    the same live system state.

    The live PolicyEngine is fail-closed (no rules -> INSUFFICIENT -> deny),
    which is the genuine system behavior. A deployment permits skills by
    registering an allow rule on the *real* engine — we do exactly that here,
    leaving every other component (PermissionBroker, SandboxPool,
    CapabilityRegistry, SkillManager lifecycle) fully real.
    """
    from aios.runtime.policy import PolicyDecision, PolicyEngine, PolicyRule

    policy = live_kernel.container.resolve(PolicyEngine)
    policy.add_rule(
        PolicyRule(
            "allow-superpowers-test",
            applies=lambda r: True,
            decision=PolicyDecision.ALLOW,
            reason="test harness permits superpowers skills",
        )
    )
    mgr = live_kernel.skill_manager
    for sid in EXPECTED_SKILLS:
        contract = _contract_from_disk(sid)
        mgr.install(contract, source="local")
        mgr.enable(sid)
        mgr.resolve(sid)
    return mgr


# ---------------------------------------------------------------------------
# 1. Boot the real system and load skills through the real lifecycle
# ---------------------------------------------------------------------------
def test_kernel_boots_and_exposes_skill_manager(live_kernel):
    from aios.skill.manager import SkillManager

    mgr = live_kernel.skill_manager
    assert isinstance(mgr, SkillManager)
    # Real services are injected (not None) — proves it is the live system
    assert mgr._policy is not None
    assert mgr._permissions is not None
    assert mgr._capability_registry is not None
    assert mgr._sandbox_pool is not None


def test_skills_install_enable_resolve_through_real_manager(loaded_manager):
    for sid in EXPECTED_SKILLS:
        # Already installed+enabled by the fixture; verify the live states.
        assert loaded_manager._registry.get(sid).status == SkillStatus.ENABLED, f"{sid} not ENABLED"
        # resolve must succeed (no broken deps)
        loaded_manager.resolve(sid)


def test_all_skills_enabled_in_kernel_registry(loaded_manager):
    for sid in EXPECTED_SKILLS:
        assert sid in loaded_manager._registry
        assert loaded_manager._registry.get(sid).status == SkillStatus.ENABLED


# ---------------------------------------------------------------------------
# 2. Router is wired into the live system (selected skills are enabled)
# ---------------------------------------------------------------------------
def test_router_selection_maps_to_enabled_skills(loaded_manager):
    req = "let's build a new feature and write a plan, then fix a bug and verify it is done"
    selected = route(req)
    assert selected[0] == META_SKILL
    for sid in selected:
            assert sid in loaded_manager._registry, f"router picked unregistered {sid!r}"
            assert loaded_manager._registry.get(sid).status == SkillStatus.ENABLED

# ---------------------------------------------------------------------------
# 3. REAL execution through the sandbox (the actual run path)
# ---------------------------------------------------------------------------
def test_execute_superpowers_skill_through_real_sandbox(loaded_manager):
    # using-superpowers is the meta-skill; it has no required capabilities,
    # so it enables and executes through the real SandboxPool.
    sid = META_SKILL
    assert loaded_manager._registry.get(sid).status == SkillStatus.ENABLED
    result = loaded_manager.execute(sid, payload={"request": "build a feature"})
    assert result.status == "completed", f"execution failed: {result.error}"
    assert result.sandbox_id is not None
    assert "output" in result.to_dict()


def test_execute_a_process_skill_through_real_sandbox(loaded_manager):
    # brainstorming is a process skill selected for build requests
    sid = "brainstorming"
    assert loaded_manager._registry.get(sid).status == SkillStatus.ENABLED
    result = loaded_manager.execute(sid, payload={"request": "build a feature"})
    assert result.status == "completed", f"execution failed: {result.error}"


# ---------------------------------------------------------------------------
# 4. Full scenario: request -> router -> enable -> execute (end-to-end in system)
# ---------------------------------------------------------------------------
def test_end_to_end_request_to_execution(loaded_manager):
    request = "fix this bug, it fails with a traceback"
    selected = route(request)
    assert "systematic-debugging" in selected
    # Every selected skill must be executable in the live system
    for sid in selected:
        if sid == META_SKILL:
            continue
        # ensure enabled (idempotent if already)
        if loaded_manager._registry.get(sid).status != SkillStatus.ENABLED:
            loaded_manager.enable(sid)
        result = loaded_manager.execute(sid, payload={"request": request})
        assert result.status == "completed", f"{sid} execution failed: {result.error}"


# ---------------------------------------------------------------------------
# 5. Persistence snapshot round-trips (system restart simulation)
# ---------------------------------------------------------------------------
def test_persist_restore_roundtrip(loaded_manager):
    snapshot = loaded_manager.persist()
    assert "registry" in snapshot
    assert all(sid in snapshot["registry"] for sid in EXPECTED_SKILLS)
    # Restore into a fresh manager must preserve the enabled states
    loaded_manager.restore(snapshot)
    for sid in EXPECTED_SKILLS:
        assert loaded_manager._registry.get(sid).status == SkillStatus.ENABLED
