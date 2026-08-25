"""End-to-end runtime-flow test for the Superpowers integration (TASK-SUPERPOWERS).

This is NOT a unit test of the router alone. It verifies the *actual* runtime
flow: the 12 AIOS-adapted skills exist on disk as well-formed artifacts, they
load and register through the real ``SkillManager`` (proving they are genuine
AIOS skills, not loose markdown), the router's selected skills all map to
registered skills, and AGENTS.md references the integration.

Run:  python -m pytest aios/skill/tests/test_superpowers_integration.py -q
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from aios.skill.manager import SkillManager
from aios.skill.contracts import SkillContract, SkillStatus
from aios.skill.superpowers_router import (
    META_SKILL,
    PROCESS_SKILLS,
    route,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills" / "superpowers" / "skills"
AGENTS_MD = REPO_ROOT / "AGENTS.md"

# The 12 skills delivered by the integration (must match generator output).
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


def _parse_frontmatter_name(skill_md: str) -> str:
    """Extract the ``name:`` field from a SKILL.md YAML frontmatter block."""
    lines = skill_md.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError("SKILL.md missing opening '---' frontmatter")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    raise AssertionError("SKILL.md frontmatter missing 'name:'")


# ---------------------------------------------------------------------------
# 1. On-disk artifact presence
# ---------------------------------------------------------------------------
def test_all_expected_skill_dirs_present():
    assert SKILLS_ROOT.is_dir(), f"skills root missing: {SKILLS_ROOT}"
    for sid in EXPECTED_SKILLS:
        d = SKILLS_ROOT / sid
        assert d.is_dir(), f"missing skill dir: {d}"
        assert (d / "SKILL.md").is_file(), f"missing SKILL.md in {sid}"
        assert (d / "manifest.json").is_file(), f"missing manifest.json in {sid}"
        assert (d / "catalog" / f"skill-{sid}.json").is_file(), f"missing catalog in {sid}"
        assert (d / "prompts" / "instructions.md").is_file(), f"missing instructions.md in {sid}"


# ---------------------------------------------------------------------------
# 2. Manifest + frontmatter validity
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("sid", EXPECTED_SKILLS)
def test_skill_manifest_and_frontmatter_valid(sid):
    d = SKILLS_ROOT / sid
    manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    # manifest self-consistency
    assert manifest["skill_id"] == sid, f"manifest skill_id mismatch in {sid}"
    assert manifest["name"] == sid, f"manifest name mismatch in {sid}"
    assert manifest["version"] == "1.0.0"
    assert manifest["entrypoint"] == "SKILL.md"
    # SKILL.md frontmatter name must match the skill id
    skill_md = (d / "SKILL.md").read_text(encoding="utf-8")
    assert _parse_frontmatter_name(skill_md) == sid, f"frontmatter name != id in {sid}"
    # catalog must point at the same skill
    catalog = json.loads((d / "catalog" / f"skill-{sid}.json").read_text(encoding="utf-8"))
    assert catalog["skill_id"] == sid


# ---------------------------------------------------------------------------
# 3. Real SkillManager load + register (the actual runtime flow)
# ---------------------------------------------------------------------------
@pytest.fixture()
def manager_with_superpowers():
    mgr = SkillManager()
    for sid in EXPECTED_SKILLS:
        manifest = json.loads((SKILLS_ROOT / sid / "manifest.json").read_text(encoding="utf-8"))
        contract = SkillContract.create(
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
        installed = mgr.install(contract, source="local")
        assert installed.status == SkillStatus.INSTALLED, f"{sid} not INSTALLED"
    return mgr


def test_skills_register_through_real_manager(manager_with_superpowers):
    mgr = manager_with_superpowers
    for sid in EXPECTED_SKILLS:
        assert sid in mgr._registry, f"{sid} not registered"
        assert mgr._registry.get(sid).status == SkillStatus.INSTALLED


# ---------------------------------------------------------------------------
# 4. Router output maps to actually-registered skills (wiring proof)
# ---------------------------------------------------------------------------
def test_router_maps_to_registered_skills(manager_with_superpowers):
    mgr = manager_with_superpowers
    scenarios = [
        "let's build a new feature and write a plan",
        "fix this bug, it fails with a traceback",
        "is it done? verify the tests pass before commit",
        "review feedback from the reviewer",
        "finish the development branch and merge",
    ]
    for req in scenarios:
        selected = route(req)
        assert selected[0] == META_SKILL
        for sid in selected:
            # every selected skill (incl. meta) must be a real registered skill
            assert sid in mgr._registry, f"router selected unregistered skill {sid!r} for {req!r}"


# ---------------------------------------------------------------------------
# 5. End-to-end scenario assertions (process priority + coverage)
# ---------------------------------------------------------------------------
def test_scenario_build_request():
    r = route("let's build a new feature and write a plan")
    assert META_SKILL in r
    assert "brainstorming" in r
    assert "writing-plans" in r
    # process skill precedes implementation skills
    assert r.index("brainstorming") < r.index("writing-plans")


def test_scenario_debug_request():
    r = route("fix this bug, it fails with a traceback")
    assert META_SKILL in r
    assert "systematic-debugging" in r
    # process skill must precede any implementation skill when both present
    impl = [s for s in r if s not in PROCESS_SKILLS and s != META_SKILL]
    if impl:
        assert r.index("systematic-debugging") < min(r.index(s) for s in impl)


def test_scenario_verify_request():
    r = route("verify the tests pass then finish development branch and merge")
    assert "verification-before-completion" in r
    assert "finishing-a-development-branch" in r


def test_scenario_review_request():
    r = route("address the review feedback from code review")
    assert "receiving-code-review" in r
    assert "requesting-code-review" in r


def test_scenario_subagent_request():
    r = route("execute plan with subagent driven development in parallel")
    assert "subagent-driven-development" in r
    assert "executing-plans" in r


# ---------------------------------------------------------------------------
# 6. AGENTS.md reference (documentation wiring)
# ---------------------------------------------------------------------------
def test_agents_md_references_integration():
    assert AGENTS_MD.is_file()
    text = AGENTS_MD.read_text(encoding="utf-8")
    assert "superpowers-integration-ref" in text
    assert "superpowers_router" in text
    assert "skills/superpowers/" in text
