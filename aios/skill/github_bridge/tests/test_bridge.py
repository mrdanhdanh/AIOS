"""Tests for the GitHub Skill -> AIOS Skill Plugin bridge (TASK-219, M11)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aios.governance.architecture.guard import ArchitectureGuard
from aios.skill.contracts import SkillStatus
from aios.skill.github_bridge import (
    convert_skill_dir,
    parse_agent_yaml,
    parse_skill_md,
    parse_skill_md_text,
    to_plugin_manifest,
    to_skill_contract,
)
from aios.skill.github_bridge.parser import discover_capabilities
from aios.skill.manager import SkillManager

_SKILL_MD = """---
name: ui-ux-pro-max
description: Design intelligence for professional UI/UX.
---
# UI/UX Pro Max

Use this skill to build professional interfaces.
Follow the design system and accessibility guidelines.
"""

_AGENT_YAML = """name: ui-ux-agent
model: gpt-4o
tools:
  - ui.render
  - ui.a11y
instructions: Apply design intelligence.
"""

_RUN_PY = "print('run skill')\n"


def _make_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "ui-ux-pro-max-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(_SKILL_MD, encoding="utf-8")
    scripts = skill / "scripts"
    scripts.mkdir()
    (scripts / "run.py").write_text(_RUN_PY, encoding="utf-8")
    agents = skill / "agents"
    agents.mkdir()
    (agents / "openai.yaml").write_text(_AGENT_YAML, encoding="utf-8")
    return skill


def test_parse_skill_md_frontmatter():
    parsed = parse_skill_md_text(_SKILL_MD)
    assert parsed["name"] == "ui-ux-pro-max"
    assert parsed["description"] == "Design intelligence for professional UI/UX."
    assert "build professional interfaces" in parsed["body"]
    assert parsed["frontmatter"]["name"] == "ui-ux-pro-max"


def test_parse_skill_md_no_frontmatter():
    parsed = parse_skill_md_text("# Just body\nDo things.\n", source_name="plain.md")
    assert parsed["name"] == "plain"
    assert "Do things." in parsed["body"]
    assert parsed["frontmatter"] == {}


def test_discover_capabilities(tmp_path):
    skill = _make_skill(tmp_path)
    caps = discover_capabilities(skill)
    assert "ui.render" in caps
    assert "ui.a11y" in caps


def test_to_skill_contract_validates(tmp_path):
    skill = _make_skill(tmp_path)
    parsed = parse_skill_md(skill / "SKILL.md")
    caps = discover_capabilities(skill)
    contract = to_skill_contract(
        parsed,
        skill_id="ui-ux-pro-max",
        required_capabilities=caps,
        entrypoint="scripts/run.py",
    )
    contract.validate()  # must not raise
    assert contract.skill_id == "ui-ux-pro-max"
    assert contract.runtime == "python3.11"
    assert "ui.render" in contract.required_capabilities


def test_to_plugin_manifest_schema(tmp_path):
    skill = _make_skill(tmp_path)
    parsed = parse_skill_md(skill / "SKILL.md")
    contract = to_skill_contract(parsed, skill_id="ui-ux-pro-max")
    plugin = to_plugin_manifest(contract)
    errs = plugin.validate()
    assert errs == []
    assert plugin.plugin_id == "ui-ux-pro-max"


def test_convert_skill_dir_writes_package(tmp_path):
    skill = _make_skill(tmp_path)
    out = tmp_path / "pkg"
    result = convert_skill_dir(skill, out, skill_id="ui-ux-pro-max")
    assert result["layout"] == "copilot"
    assert len(result["skills"]) == 1
    sub = out / "skills" / "ui-ux-pro-max"
    assert (sub / "manifest.json").is_file()
    assert (sub / "prompts" / "instructions.md").is_file()
    assert (sub / "SKILL.md").is_file()
    assert (sub / "plugin_manifest.json").is_file()
    assert (sub / "catalog" / "skill-ui-ux-pro-max.json").is_file()
    assert (out / "package_index.json").is_file()
    assert (out / "source" / "SKILL.md").is_file()

    manifest = json.loads((sub / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["skill_id"] == "ui-ux-pro-max"
    assert "ui.render" in manifest["required_capabilities"]


def test_convert_then_install_enable(tmp_path):
    skill = _make_skill(tmp_path)
    out = tmp_path / "pkg"
    result = convert_skill_dir(skill, out, skill_id="ui-ux-pro-max")
    contract = result["skills"][0]["contract"]

    mgr = SkillManager()  # no injected runtime services -> offline default
    installed = mgr.install(contract, source="git")
    assert installed.status == SkillStatus.INSTALLED
    enabled = mgr.enable("ui-ux-pro-max")
    assert enabled.status == SkillStatus.ENABLED


def test_deterministic_conversion(tmp_path):
    skill = _make_skill(tmp_path)
    out1 = tmp_path / "pkg1"
    out2 = tmp_path / "pkg2"
    convert_skill_dir(skill, out1, skill_id="ui-ux-pro-max")
    convert_skill_dir(skill, out2, skill_id="ui-ux-pro-max")
    m1 = (out1 / "skills" / "ui-ux-pro-max" / "manifest.json").read_bytes()
    m2 = (out2 / "skills" / "ui-ux-pro-max" / "manifest.json").read_bytes()
    assert m1 == m2


def test_architecture_clean():
    pkg_dir = Path(__file__).resolve().parent.parent
    guard = ArchitectureGuard(roots=[str(pkg_dir)])
    result = guard.check()
    assert result.passed, f"architecture violations: {result.violations}"
