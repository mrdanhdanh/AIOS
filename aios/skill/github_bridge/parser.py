"""Parse a GitHub Copilot skill into structured data (TASK-219, M11).

A Copilot skill is a directory containing ``SKILL.md`` (YAML frontmatter with
``name``/``description`` + a markdown instruction body) and optionally
``scripts/`` (executable helpers) and ``agents/`` (agent definitions, e.g.
``openai.yaml`` listing ``tools``/``capabilities``).

Layering: ``skill`` layer — stdlib + ``aios.core`` only. No ``subprocess``/``os``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is a core runtime dep
    yaml = None  # type: ignore[assignment]

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


class SkillParseError(Exception):
    """Raised when a GitHub skill cannot be parsed (fail-closed)."""


def parse_skill_md_text(text: str, source_name: str = "SKILL.md") -> Dict[str, Any]:
    """Parse SKILL.md text into ``{name, description, body, frontmatter}``."""
    if not isinstance(text, str):
        raise SkillParseError(f"SKILL.md content must be str, got {type(text).__name__}")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        # No frontmatter: treat the whole file as the instruction body and
        # derive a name from the source filename.
        return {
            "name": source_name.rsplit(".", 1)[0] or "github-skill",
            "description": "",
            "body": text.strip(),
            "frontmatter": {},
        }
    fm_text, body = m.group(1), m.group(2)
    if yaml is None:
        raise SkillParseError("PyYAML is required to parse SKILL.md frontmatter")
    try:
        fm = yaml.safe_load(fm_text) or {}
    except Exception as exc:  # noqa: BLE001 - surface parse errors clearly
        raise SkillParseError(f"Invalid YAML frontmatter in {source_name}: {exc}") from exc
    if not isinstance(fm, dict):
        raise SkillParseError(f"SKILL.md frontmatter must be a mapping in {source_name}")
    return {
        "name": str(fm.get("name", source_name.rsplit(".", 1)[0] or "github-skill")),
        "description": str(fm.get("description", "")),
        "body": body.strip(),
        "frontmatter": fm,
    }


def parse_skill_md(path: str | Path) -> Dict[str, Any]:
    """Read and parse a ``SKILL.md`` file from disk."""
    p = Path(path)
    if not p.is_file():
        raise SkillParseError(f"SKILL.md not found: {p}")
    return parse_skill_md_text(p.read_text(encoding="utf-8"), source_name=p.name)


def parse_agent_yaml(path: str | Path) -> Dict[str, Any]:
    """Parse an agent definition YAML (e.g. ``agents/openai.yaml``)."""
    p = Path(path)
    if not p.is_file():
        raise SkillParseError(f"Agent yaml not found: {p}")
    if yaml is None:
        raise SkillParseError("PyYAML is required to parse agent yaml")
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        raise SkillParseError(f"Invalid YAML in {p.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise SkillParseError(f"Agent yaml must be a mapping in {p.name}")
    return data


def discover_capabilities(skill_dir: str | Path) -> List[str]:
    """Collect capability/tool names declared by agent definitions."""
    skill_dir = Path(skill_dir)
    caps: List[str] = []
    agents_dir = skill_dir / "agents"
    if not agents_dir.is_dir():
        return caps
    for yf in sorted(agents_dir.glob("*.yaml")) + sorted(agents_dir.glob("*.yml")):
        try:
            data = parse_agent_yaml(yf)
        except SkillParseError:
            continue
        for key in ("tools", "capabilities"):
            for item in data.get(key) or []:
                if isinstance(item, str) and item not in caps:
                    caps.append(item)
    return caps


def parse_skill_json(path: str | Path) -> Dict[str, Any]:
    """Parse a package-level ``skill.json`` (Claude/Cursor skill package)."""
    p = Path(path)
    if not p.is_file():
        raise SkillParseError(f"skill.json not found: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        raise SkillParseError(f"Invalid JSON in {p.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise SkillParseError(f"skill.json must be a mapping in {p.name}")
    return data


def detect_skill_layout(skill_dir: str | Path) -> str:
    """Return the detected skill layout.

    * ``copilot``  — single ``SKILL.md`` at the root.
    * ``claude``   — ``skill.json`` + ``.claude/skills/<name>/SKILL.md`` (multi-skill).
    * ``unknown``  — neither found.
    """
    skill_dir = Path(skill_dir)
    if (skill_dir / "SKILL.md").is_file():
        return "copilot"
    if (skill_dir / "skill.json").is_file() and (skill_dir / ".claude" / "skills").is_dir():
        return "claude"
    return "unknown"


def parse_skill_package(skill_dir: str | Path) -> Dict[str, Any]:
    """Parse a GitHub skill directory into a normalized package descriptor.

    Supports both the Copilot layout (single root ``SKILL.md``) and the Claude
    package layout (``skill.json`` + ``.claude/skills/<name>/SKILL.md``). Returns
    ``{layout, package, skills:[{id, name, description, body, frontmatter, path}]}``.
    """
    skill_dir = Path(skill_dir)
    if not skill_dir.is_dir():
        raise SkillParseError(f"Skill directory not found: {skill_dir}")

    layout = detect_skill_layout(skill_dir)
    package: Dict[str, Any] = {}
    skills: List[Dict[str, Any]] = []

    if layout == "copilot":
        parsed = parse_skill_md(skill_dir / "SKILL.md")
        skills.append({**parsed, "id": _slugify(parsed["name"]), "path": str(skill_dir / "SKILL.md")})
    elif layout == "claude":
        package = parse_skill_json(skill_dir / "skill.json")
        skills_root = skill_dir / ".claude" / "skills"
        for sk in sorted(skills_root.iterdir()):
            sk_md = sk / "SKILL.md"
            if not sk_md.is_file():
                continue
            parsed = parse_skill_md(sk_md)
            skills.append({**parsed, "id": _slugify(parsed["name"]), "path": str(sk_md)})
    else:
        raise SkillParseError(
            f"Unrecognized skill layout in {skill_dir}: expected SKILL.md or skill.json+.claude/skills"
        )

    return {"layout": layout, "package": package, "skills": skills}


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-\.]", "-", (name or "").strip().lower())
    s = re.sub(r"-+", "-", s).strip("-.")
    return s or "github-skill"
