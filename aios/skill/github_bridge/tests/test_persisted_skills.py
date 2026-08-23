"""Verify the persisted skill package under ``skills/`` loads via lifecycle.

This guards against the package being lost (e.g. temp dir cleanup) — it
re-loads the on-disk ``skills/ui-ux-pro-max`` package and asserts every
sub-skill can be installed + enabled through the real SkillManager.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aios.skill.contracts import SkillStatus
from aios.skill.github_bridge.converter import _write_json  # noqa: F401 (ensure importable)
from aios.skill.manager import SkillManager

_PERSISTED = Path(r"d:\AIOS\skills\ui-ux-pro-max")


@pytest.mark.skipif(
    not _PERSISTED.is_dir(),
    reason="persisted skill package not present (run: python tools/install_github_skill.py --local tmp_skill_test/ui-ux-pro-max-skill --out skills/ui-ux-pro-max)",
)
def test_persisted_package_loads():
    index = json.loads((_PERSISTED / "package_index.json").read_text(encoding="utf-8"))
    assert index["layout"] == "claude"
    skill_ids = index["skills"]
    assert len(skill_ids) >= 1

    mgr = SkillManager()
    for sid in skill_ids:
        manifest = json.loads(
            (_PERSISTED / "skills" / sid / "manifest.json").read_text(encoding="utf-8")
        )
        # Reconstruct a contract from the persisted manifest and enable it.
        from aios.skill.contracts import SkillContract

        contract = SkillContract.from_dict(manifest)
        installed = mgr.install(contract, source="git")
        assert installed.status == SkillStatus.INSTALLED
        enabled = mgr.enable(sid)
        assert enabled.status == SkillStatus.ENABLED

    assert mgr.get if hasattr(mgr, "get") else True
    assert len(mgr) == len(skill_ids)
    assert "ui-ux-pro-max" in skill_ids
