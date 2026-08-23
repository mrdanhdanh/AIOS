"""GitHub Skill -> AIOS Skill Plugin bridge (TASK-219, M11).

Converts a GitHub Copilot skill (``SKILL.md`` + ``scripts/`` + ``agents/``)
into an AIOS ``SkillContract`` (and a schema-compatible ``PluginManifest``),
so it can be loaded through the existing skill lifecycle
(``SkillManager.install`` -> ``enable``).

Layering: ``skill`` layer — stdlib + ``aios.core`` + ``aios.skill`` +
``aios.plugin_runtime`` (unknown) only. Never imports ``runtime`` internals,
``agent``, ``orchestrator``, ``capability`` internals, ``subprocess`` or ``os``.
"""

from __future__ import annotations

from .adapter import to_plugin_manifest, to_skill_contract
from .converter import convert_skill_dir
from .parser import (
    SkillParseError,
    detect_skill_layout,
    discover_capabilities,
    parse_agent_yaml,
    parse_skill_json,
    parse_skill_md,
    parse_skill_md_text,
    parse_skill_package,
)

__all__ = [
    "parse_skill_md",
    "parse_skill_md_text",
    "parse_skill_json",
    "parse_skill_package",
    "detect_skill_layout",
    "parse_agent_yaml",
    "discover_capabilities",
    "SkillParseError",
    "to_skill_contract",
    "to_plugin_manifest",
    "convert_skill_dir",
]
