"""Parse a GitHub Copilot skill into structured data (TASK-219, M11).

A Copilot skill is a directory containing ``SKILL.md`` (YAML frontmatter with
``name``/``description`` + a markdown instruction body) and optionally
``scripts/`` (executable helpers) and ``agents/`` (agent definitions, e.g.
``openai.yaml`` listing ``tools``/``capabilities``).

Layering: ``skill`` layer — stdlib + ``aios.core`` only. No ``subprocess``/``os``.
"""

from __future__ import annotations

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
