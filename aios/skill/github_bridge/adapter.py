"""Map parsed GitHub skill data to AIOS contracts (TASK-219, M11).

Produces a ``SkillContract`` (aios.skill) and a schema-compatible
``PluginManifest`` (aios.plugin_runtime) so the converted skill can be loaded
through the existing skill lifecycle and optionally registered as a plugin.

Layering: ``skill`` layer — stdlib + ``aios.core`` + ``aios.skill`` +
``aios.plugin_runtime`` (unknown) only. No ``subprocess``/``os``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from aios.plugin_runtime.manifest import PluginManifest
from aios.skill.contracts import (
    ALLOWED_PERMISSIONS,
    ALLOWED_RUNTIMES,
    SkillContract,
    SkillError,
)

# Map common Copilot permission hints to AIOS allowed permissions.
_PERMISSION_HINTS: Dict[str, str] = {
    "filesystem.read": "filesystem.read",
    "filesystem.write": "filesystem.write",
    "network": "network.read",
    "network.read": "network.read",
    "network.write": "network.write",
    "process": "process.execute",
    "process.execute": "process.execute",
    "memory": "memory:read",
    "memory.read": "memory:read",
    "memory.write": "memory:write",
    "tool": "tool:invoke",
    "tool.invoke": "tool:invoke",
    "capability": "capability:invoke",
    "capability.invoke": "capability:invoke",
    "skill": "skill:invoke",
    "skill.invoke": "skill:invoke",
}


def _normalize_permissions(perms: List[str]) -> List[str]:
    out: List[str] = []
    for p in perms or []:
        p = p.strip()
        if not p:
            continue
        mapped = _PERMISSION_HINTS.get(p, p)
        if mapped in ALLOWED_PERMISSIONS and mapped not in out:
            out.append(mapped)
    return out


def _normalize_runtime(runtime: str) -> str:
    rt = (runtime or "").strip().lower()
    if rt in ALLOWED_RUNTIMES:
        return rt
    if rt.startswith("python3.11") or rt in ("python", "python3"):
        return "python3.11"
    if rt.startswith("node20") or rt in ("node", "nodejs"):
        return "node20"
    return "python3.11"


def to_skill_contract(
    parsed: Dict[str, Any],
    *,
    skill_id: str,
    version: str = "1.0.0",
    runtime: str = "python3.11",
    permissions: Optional[List[str]] = None,
    required_capabilities: Optional[List[str]] = None,
    entrypoint: str = "",
    install_source: str = "git",
    author: str = "",
) -> SkillContract:
    """Build a validated ``SkillContract`` from parsed skill data."""
    if not skill_id or not skill_id.strip():
        raise SkillError("skill_id must be non-empty")
    perms = _normalize_permissions(permissions or [])
    rt = _normalize_runtime(runtime)
    resources = {"instructions_chars": len(parsed.get("body", "") or "")}
    return SkillContract.create(
        skill_id=skill_id,
        name=parsed.get("name", skill_id),
        version=version,
        description=parsed.get("description", ""),
        author=author,
        dependencies=[],
        required_capabilities=required_capabilities or [],
        permissions=perms,
        resources=resources,
        runtime=rt,
        entrypoint=entrypoint,
        install_source=install_source,
        install_location=f"/skills/{skill_id}/{version}",
        metadata={
            "source": "github-copilot-skill",
            "frontmatter": parsed.get("frontmatter", {}),
        },
    )


def to_plugin_manifest(
    contract: SkillContract,
    *,
    capabilities: Optional[List[str]] = None,
) -> PluginManifest:
    """Build a schema-compatible ``PluginManifest`` from a skill contract."""
    return PluginManifest(
        plugin_id=contract.skill_id,
        name=contract.name,
        version=contract.version,
        capabilities=capabilities or contract.required_capabilities or [contract.skill_id],
        dependencies=[],
        min_runtime_version="1.0.0",
    )
