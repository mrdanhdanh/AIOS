"""Prompt Registry — versioned deterministic templates (TASK-009, M1).

M1 uses a tiny ``str.format`` subset: placeholders are ``{identifier}`` where
identifier matches ``[a-zA-Z_][a-zA-Z0-9_]*``.  Rendering is deterministic and
fail-closed on missing variables — no silent placeholder dropping.

No Jinja2 in M1 (per roadmap it ships later). No LLM, no network.

Layering: ``capability`` layer — stdlib + ``aios.core`` only.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from aios.core.version import SemVer, VersionError

__all__ = ["PromptError", "PromptContract", "PromptRegistry"]

_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
_PROMPT_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_\-]*$")


class PromptError(Exception):
    """Raised on prompt validation or registry errors."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_variables(template: str) -> List[str]:
    return _PLACEHOLDER_RE.findall(template)


def _validate_template(template: str) -> None:
    if not isinstance(template, str) or not template.strip():
        raise PromptError("template must be a non-empty string")
    # reject stray braces that are not part of a valid placeholder
    # by ensuring every '{' ... '}' matches the placeholder pattern.
    # We scan for braces: any '{' that is not followed by a valid identifier
    # and '}' is considered invalid.  Escaped '{{' / '}}' not supported in M1.
    # Simpler: find all {...} groups and ensure they match placeholder form.
    brace_groups = re.findall(r"\{[^}]+\}", template)
    for g in brace_groups:
        if not _PLACEHOLDER_RE.fullmatch(g):
            raise PromptError(f"invalid placeholder {g!r} — expected {{identifier}}")


@dataclass
class PromptContract:
    """Versioned prompt template."""

    prompt_id: str
    version: str = "1.0.0"
    template: str = ""
    variables: List[str] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, object] = field(default_factory=dict)
    source: str = ""
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def create(
        cls,
        prompt_id: str,
        template: str,
        version: str = "1.0.0",
        description: str = "",
        metadata: Optional[Dict[str, object]] = None,
        source: str = "",
    ) -> "PromptContract":
        variables = _extract_variables(template)
        obj = cls(
            prompt_id=prompt_id,
            version=version,
            template=template,
            variables=variables,
            description=description,
            metadata=dict(metadata or {}),
            source=source or "",
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if not isinstance(self.prompt_id, str) or not self.prompt_id.strip():
            raise PromptError("prompt_id must be a non-empty string")
        if not _PROMPT_ID_RE.match(self.prompt_id):
            raise PromptError(
                f"prompt_id {self.prompt_id!r} must match {_PROMPT_ID_RE.pattern}"
            )
        try:
            SemVer.parse(self.version)
        except VersionError as exc:
            raise PromptError(f"Invalid version {self.version!r}: {exc}") from exc
        _validate_template(self.template)
        # variables must be consistent with template
        expected = _extract_variables(self.template)
        if sorted(self.variables) != sorted(expected):
            raise PromptError(
                f"variables {self.variables!r} inconsistent with template placeholders {expected!r}"
            )
        # variables entries must be valid identifiers
        for v in self.variables:
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", v):
                raise PromptError(f"variable {v!r} must be a valid identifier")

    def render(self, **kwargs: object) -> str:
        """Deterministically render the template.

        Raises :class:`PromptError` if any required variable is missing.
        Extra variables are ignored (callers may pass superset).
        """
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise PromptError(f"Missing variables for prompt {self.prompt_id!r}: {missing}")
        # Use str.format with only the declared variables (deterministic)
        mapping = {k: kwargs[k] for k in self.variables}
        try:
            return self.template.format(**mapping)
        except KeyError as exc:
            raise PromptError(f"Missing variable {exc.args[0]!r}") from exc

    def to_dict(self) -> Dict[str, object]:
        return {
            "prompt_id": self.prompt_id,
            "version": self.version,
            "template": self.template,
            "variables": list(self.variables),
            "description": self.description,
            "metadata": dict(self.metadata),
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PromptRegistry:
    """Thread-safe registry of :class:`PromptContract` keyed by (prompt_id, version)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # prompt_id -> {version -> contract}
        self._store: Dict[str, Dict[str, PromptContract]] = {}

    def register(self, contract: PromptContract) -> None:
        if not isinstance(contract, PromptContract):
            raise PromptError("contract must be PromptContract")
        contract.validate()
        with self._lock:
            bucket = self._store.setdefault(contract.prompt_id, {})
            if contract.version in bucket:
                raise PromptError(
                    f"prompt {contract.prompt_id!r} version {contract.version!r} already registered"
                )
            bucket[contract.version] = contract

    def get(self, prompt_id: str, version: Optional[str] = None) -> PromptContract:
        with self._lock:
            bucket = self._store.get(prompt_id)
            if bucket is None or not bucket:
                raise PromptError(f"unknown prompt: {prompt_id!r}")
            if version is not None:
                c = bucket.get(version)
                if c is None:
                    raise PromptError(
                        f"prompt {prompt_id!r} has no version {version!r}; available: {sorted(bucket)}"
                    )
                return c
            # no version → latest SemVer
            latest = max(bucket.values(), key=lambda c: SemVer.parse(c.version))
            return latest

    def list(self, prompt_id: Optional[str] = None) -> List[PromptContract]:
        with self._lock:
            if prompt_id is not None:
                bucket = self._store.get(prompt_id, {})
                return sorted(bucket.values(), key=lambda c: SemVer.parse(c.version))
            out: List[PromptContract] = []
            for bucket in self._store.values():
                out.extend(bucket.values())
            return sorted(out, key=lambda c: (c.prompt_id, SemVer.parse(c.version)))

    def versions(self, prompt_id: str) -> List[str]:
        with self._lock:
            bucket = self._store.get(prompt_id)
            if bucket is None:
                raise PromptError(f"unknown prompt: {prompt_id!r}")
            return sorted(bucket.keys(), key=lambda v: SemVer.parse(v))

    def render(self, prompt_id: str, version: Optional[str] = None, **kwargs: object) -> str:
        return self.get(prompt_id, version).render(**kwargs)

    def remove(self, prompt_id: str, version: Optional[str] = None) -> None:
        with self._lock:
            bucket = self._store.get(prompt_id)
            if bucket is None:
                raise PromptError(f"unknown prompt: {prompt_id!r}")
            if version is not None:
                if version not in bucket:
                    raise PromptError(f"prompt {prompt_id!r} has no version {version!r}")
                del bucket[version]
                if not bucket:
                    del self._store[prompt_id]
            else:
                del self._store[prompt_id]

    def __len__(self) -> int:
        with self._lock:
            return sum(len(b) for b in self._store.values())

    def __contains__(self, prompt_id: str) -> bool:
        with self._lock:
            return prompt_id in self._store

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
