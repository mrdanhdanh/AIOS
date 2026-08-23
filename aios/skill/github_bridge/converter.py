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
from .parser import (
    SkillParseError,
    detect_skill_layout,
    discover_capabilities,
    parse_skill_md,
    parse_skill_package,
)


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
    """Convert a GitHub skill directory into an AIOS skill package on disk.

    Supports both layouts:
      * Copilot  — single root ``SKILL.md`` -> one skill package.
      * Claude   — ``skill.json`` + ``.claude/skills/<name>/SKILL.md`` ->
        one package containing multiple sub-skills (each its own contract).

    Returns ``{layout, package_dir, skills:[{skill_id, contract, plugin_manifest}]}``.
    """
    skill_dir = Path(skill_dir)
    out_dir = Path(out_dir)
    if not skill_dir.is_dir():
        raise GitHubSkillConvertError(f"Skill directory not found: {skill_dir}")

    layout = detect_skill_layout(skill_dir)
    if layout == "unknown":
        raise GitHubSkillConvertError(
            f"Unrecognized skill layout in {skill_dir}: expected SKILL.md or skill.json+.claude/skills"
        )

    pkg = parse_skill_package(skill_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy the whole source skill verbatim as a reference bundle.
    ref_dir = out_dir / "source"
    if ref_dir.exists():
        shutil.rmtree(ref_dir)
    shutil.copytree(skill_dir, ref_dir, ignore=shutil.ignore_patterns(".git"))

    skills_out: List[Dict[str, Any]] = []
    for sk in pkg["skills"]:
        sid = sk["id"]
        sub_out = out_dir / "skills" / sid
        sub_out.mkdir(parents=True, exist_ok=True)

        caps = discover_capabilities(Path(sk["path"]).parent)
        # Instruction-only skills have no executable script; use the SKILL.md
        # file itself as the entrypoint so the lifecycle's entrypoint check
        # passes (the skill is a prompt/instruction package).
        entrypoint = _discover_entrypoint(Path(sk["path"]).parent)
        if not entrypoint:
            entrypoint = "SKILL.md"
        contract = to_skill_contract(
            sk,
            skill_id=sid,
            version=version,
            runtime=runtime,
            permissions=permissions,
            required_capabilities=caps,
            entrypoint=entrypoint,
            install_source=install_source,
            author=author or pkg["package"].get("author", ""),
        )

        manifest_dict = contract.to_dict()
        manifest_dict.pop("created_at", None)
        manifest_dict.pop("updated_at", None)
        _write_json(sub_out / "manifest.json", manifest_dict)

        prompts_dir = sub_out / "prompts"
        prompts_dir.mkdir(exist_ok=True)
        (prompts_dir / "instructions.md").write_text(sk.get("body", ""), encoding="utf-8")

        # Copy the original SKILL.md so the entrypoint ("SKILL.md") resolves.
        shutil.copyfile(Path(sk["path"]), sub_out / "SKILL.md")

        plugin = to_plugin_manifest(contract)
        _write_json(sub_out / "plugin_manifest.json", plugin.to_dict())

        catalog = {
            "kind": "skill",
            "skill_id": sid,
            "name": contract.name,
            "version": contract.version,
            "source": install_source,
            "layout": layout,
            "manifest_path": "manifest.json",
            "plugin_manifest_path": "plugin_manifest.json",
        }
        catalog_dir = sub_out / "catalog"
        catalog_dir.mkdir(exist_ok=True)
        _write_json(catalog_dir / f"skill-{sid}.json", catalog)

        skills_out.append(
            {"skill_id": sid, "contract": contract, "plugin_manifest": plugin}
        )

    # Package-level index for the ecosystem registry.
    index = {
        "kind": "skill-package",
        "layout": layout,
        "source": install_source,
        "package": pkg["package"],
        "skills": [s["skill_id"] for s in skills_out],
    }
    _write_json(out_dir / "package_index.json", index)

    return {
        "layout": layout,
        "package_dir": str(out_dir),
        "skills": skills_out,
    }
