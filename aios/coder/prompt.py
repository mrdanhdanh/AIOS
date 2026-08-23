"""Prompt Architecture + PromptBuilder + Versioning (TASK-133, M19).

A small prompt architecture for the coder subsystem: versioned prompt
templates, a deterministic builder that renders a template with variables, and
an immutable version registry (T001 Rule 1). Rendering is deterministic (same
template + same variables -> same prompt). Every built prompt carries a
``content_hash`` (T078) and provenance (T001 Rule 5).
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class PromptError(Exception):
    """Raised on prompt contract violations (fail-closed, T001/T078)."""


@dataclass(frozen=True)
class PromptTemplate:
    template_id: str
    version: str
    body: str
    created_at: str

    def variables(self) -> List[str]:
        return re.findall(r"\{\{(\w+)\}\}", self.body)


@dataclass
class BuiltPrompt:
    prompt_id: str
    template_id: str
    version: str
    content: str
    content_hash: str
    evidence_id: str

    def to_dict(self) -> dict:
        return {
            "prompt_id": self.prompt_id,
            "template_id": self.template_id,
            "version": self.version,
            "content": self.content,
            "content_hash": self.content_hash,
            "evidence_id": self.evidence_id,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class PromptRegistry:
    """Versioned, immutable prompt template registry (T133 / T001 Rule 1)."""

    def __init__(self) -> None:
        # key: (template_id, version) -> PromptTemplate (immutable once stored)
        self._templates: Dict[tuple, PromptTemplate] = {}

    def register(self, template_id: str, version: str, body: str) -> PromptTemplate:
        key = (template_id, version)
        if key in self._templates:
            raise PromptError(f"template {template_id} v{version} already exists (T001 Rule 1).")
        tpl = PromptTemplate(
            template_id=template_id,
            version=version,
            body=body,
            created_at=_now(),
        )
        self._templates[key] = tpl
        return tpl

    def get(self, template_id: str, version: str) -> PromptTemplate:
        key = (template_id, version)
        if key not in self._templates:
            raise PromptError(f"unknown template {template_id} v{version}.")
        return self._templates[key]

    def latest(self, template_id: str) -> Optional[PromptTemplate]:
        versions = [t for (tid, _), t in self._templates.items() if tid == template_id]
        if not versions:
            return None
        return max(versions, key=lambda t: t.version)


class PromptBuilder:
    """Deterministic prompt builder (T133)."""

    def __init__(self, registry: PromptRegistry) -> None:
        self._registry = registry

    def build(self, template_id: str, version: str, variables: Dict[str, str]) -> BuiltPrompt:
        tpl = self._registry.get(template_id, version)
        missing = [v for v in tpl.variables() if v not in variables]
        if missing:
            raise PromptError(f"missing variables: {missing}")
        try:
            content = tpl.body
            for k, v in variables.items():
                content = content.replace(f"{{{{{k}}}}}", v)
        except Exception as exc:  # pragma: no cover - defensive
            raise PromptError(f"render failed: {exc}") from exc
        # Detect any unresolved placeholders -> fail-closed (T078).
        if re.search(r"\{\{\w+\}\}", content):
            raise PromptError("unresolved placeholder after render (T078).")
        return BuiltPrompt(
            prompt_id=f"prompt-{uuid.uuid4().hex[:12]}",
            template_id=template_id,
            version=version,
            content=content,
            content_hash=_hash(content),
            evidence_id=f"ev-{uuid.uuid4().hex[:12]}",
        )
