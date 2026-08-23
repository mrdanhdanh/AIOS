"""Real-world integration test: convert + load the cloned GitHub skill (TASK-219).

This test exercises the bridge against an actual third-party skill layout
(Claude package: ``skill.json`` + ``.claude/skills/<name>/SKILL.md``), proving
the converter + skill lifecycle work end-to-end without a network call.

The cloned skill is expected at ``tmp_skill_test/ui-ux-pro-max-skill`` (populated
by the developer / CI before running). If absent, the test is skipped.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aios.skill.contracts import SkillStatus
from aios.skill.github_bridge import (
    convert_skill_dir,
    detect_skill_layout,
    parse_skill_package,
)
from aios.skill.manager import SkillManager

_CLONED_SKILL = Path(r"d:\AIOS\tmp_skill_test\ui-ux-pro-max-skill")


@pytest.mark.skipif(
    not _CLONED_SKILL.is_dir(),
    reason="cloned skill not present (run: git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill tmp_skill_test/ui-ux-pro-max-skill)",
)
def test_cloned_skill_layout_detection():
    assert _CLONED_SKILL.is_dir()
    layout = detect_skill_layout(_CLONED_SKILL)
    assert layout == "claude"


@pytest.mark.skipif(
    not _CLONED_SKILL.is_dir(),
    reason="cloned skill not present",
)
def test_parse_cloned_skill_package():
    pkg = parse_skill_package(_CLONED_SKILL)
    assert pkg["layout"] == "claude"
    assert pkg["package"].get("name") == "ui-ux-pro-max"
    # The package contains multiple sub-skills (ui-ux-pro-max, brand, design, ...)
    assert len(pkg["skills"]) >= 1
    names = {s["name"] for s in pkg["skills"]}
    assert "ui-ux-pro-max" in names


@pytest.mark.skipif(
    not _CLONED_SKILL.is_dir(),
    reason="cloned skill not present",
)
def test_convert_and_load_cloned_skill(tmp_path):
    out = tmp_path / "pkg"
    result = convert_skill_dir(_CLONED_SKILL, out, install_source="git")
    assert result["layout"] == "claude"
    assert (out / "package_index.json").is_file()
    assert (out / "source" / "skill.json").is_file()

    # Install + enable every converted sub-skill through the real lifecycle.
    mgr = SkillManager()
    installed_ids = []
    for sk in result["skills"]:
        contract = sk["contract"]
        installed = mgr.install(contract, source="git")
        assert installed.status == SkillStatus.INSTALLED
        enabled = mgr.enable(contract.skill_id)
        assert enabled.status == SkillStatus.ENABLED
        installed_ids.append(contract.skill_id)

    # The primary skill must be present and enabled.
    assert "ui-ux-pro-max" in installed_ids
    primary = [s for s in result["skills"] if s["skill_id"] == "ui-ux-pro-max"][0]
    assert primary["contract"].status.value == "enabled"
    assert len(mgr) == len(result["skills"])
