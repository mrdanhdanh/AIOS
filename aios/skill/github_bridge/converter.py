"""Convert a GitHub Copilot skill directory into an AIOS skill package (TASK-219, M11).

The converter is deterministic: the same input skill directory always produces
the same package files (stable JSON, sorted keys). It writes:

    manifest.json          -> SkillContract dict
    prompts/instructions.md-> SKILL.md body (instructions)
    scripts/               -> copied verbatim from the source skill
    SKILL.md               -> copied as a reference
    plugin_manifest.json   -> PluginManifest dict
    catalog/skill-<id>.json-> ecosystem catalog entry

Layering: ``skill`` layer — stdlib + ``aios.core`` + ``aios.skill`` +
``aios.plugin_runtime`` (unknown) only. No ``subprocess``/``os`` (use pathlib/shutil).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .adapter import to_plugin_manifest, to_skill_contract
from .parser import SkillParseError, discover_capabilities, parse_skill_md


class GitHubSkillConvertError(Exception):
    """Raised when a GitHub skill cannot be converted (fail-closed)."""


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-\.]", "-", (name or "").strip().lower())
    s = re.sub(r"-+", "-", s).strip("-.")
    return s or "github-skill"


def _discover_entrypoint(skill_dir: Path) -> str:
    """Pick a default entrypoint: first ``scripts/*.py`` else root ``*.py``."""
    scripts = sorted(skill_dir.glob("scripts/*.py"))
    if scripts:
        return str(scripts[0].relative_to(skill_dir)).replace("\\", "/")
    roots = sorted(skill_dir.glob("*.py"))
    if roots:
        return str(roots[0].relative_to(skill_dir)).replace("\\", "/")
    return ""


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True, default=str),
        encoding="utf-8",
    )


def convert_skill_dir(
    skill_dir: str | Path,
    out_dir: str | Path,
    *,
    skill_id: Optional[str] = None,
    version: str = "1.0.0",
    runtime: str = "python3.11",
    permissions: Optional[List[str]] = None,
    author: str = "",
    install_source: str = "git",
) -> Dict[str, Any]:
    """Convert a GitHub skill directory into an AIOS skill package on disk."""
    skill_dir = Path(skill_dir)
    out_dir = Path(out_dir)
    if not skill_dir.is_dir():
        raise GitHubSkillConvertError(f"Skill directory not found: {skill_dir}")
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise GitHubSkillConvertError(f"No SKILL.md in {skill_dir}")

    parsed = parse_skill_md(skill_md)
    sid = skill_id or _slugify(parsed.get("name", skill_dir.name))
    entrypoint = _discover_entrypoint(skill_dir)
    caps = discover_capabilities(skill_dir)

    contract = to_skill_contract(
        parsed,
        skill_id=sid,
        version=version,
        runtime=runtime,
        permissions=permissions,
        required_capabilities=caps,
        entrypoint=entrypoint,
        install_source=install_source,
        author=author,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    # Drop runtime-generated timestamps so the on-disk package is fully
    # deterministic (same input skill -> identical manifest bytes). They are
    # regenerated when the skill is installed via SkillManager.
    manifest_dict = contract.to_dict()
    manifest_dict.pop("created_at", None)
    manifest_dict.pop("updated_at", None)
    _write_json(out_dir / "manifest.json", manifest_dict)

    prompts_dir = out_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    (prompts_dir / "instructions.md").write_text(
        parsed.get("body", ""), encoding="utf-8"
    )

    src_scripts = skill_dir / "scripts"
    if src_scripts.is_dir():
        dst_scripts = out_dir / "scripts"
        if dst_scripts.exists():
            shutil.rmtree(dst_scripts)
        shutil.copytree(src_scripts, dst_scripts)

    shutil.copyfile(skill_md, out_dir / "SKILL.md")

    plugin = to_plugin_manifest(contract)
    _write_json(out_dir / "plugin_manifest.json", plugin.to_dict())

    catalog = {
        "kind": "skill",
        "skill_id": sid,
        "name": contract.name,
        "version": contract.version,
        "source": install_source,
        "manifest_path": "manifest.json",
        "plugin_manifest_path": "plugin_manifest.json",
    }
    catalog_dir = out_dir / "catalog"
    catalog_dir.mkdir(exist_ok=True)
    _write_json(catalog_dir / f"skill-{sid}.json", catalog)

    return {
        "skill_id": sid,
        "contract": contract,
        "plugin_manifest": plugin,
        "package_dir": str(out_dir),
    }
