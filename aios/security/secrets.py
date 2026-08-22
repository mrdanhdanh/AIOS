"""Secret handling — scoped refs, never plaintext (TASK-070).

Secrets are stored **only** as scoped references plus a value held privately by
the :class:`SecretStore`. The value is never placed in a :class:`SecurityContext`
and is scrubbed from any log record / message via :meth:`SecretStore.redact`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Patterns that look like ``key=value`` secret assignments in log text.
# group(1) = the key/prefix, group(2) = the secret value to redact.
_SECRET_PATTERNS: List[re.Pattern[str]] = [
    re.compile(
        r"(?i)(api[_-]?key|secret|token|password|passwd|pwd|access[_-]?token)"
        r"\s*[:=]\s*['\"]?([\w\-./+]{4,})['\"]?"
    ),
    re.compile(r"(?i)(bearer)\s+([\w\-.]+\.[\w\-.]+\.[\w\-.]+)"),
    re.compile(r"(?i)(authorization)\s*[:=]\s*['\"]?([\w\-.]+\.[\w\-.]+\.[\w\-.]+)"),
]


@dataclass
class SecretRef:
    """A scoped reference to a secret. The value is NEVER stored on the ref."""

    ref_id: str
    scope: str = "default"
    kind: str = "generic"
    _value: str = field(default="", repr=False, compare=False)


class SecretError(Exception):
    """Raised on secret-store errors."""


def redact_message(text: str) -> str:
    """Standalone redaction of obvious ``key=value`` secret assignments."""
    for pat in _SECRET_PATTERNS:
        text = pat.sub(lambda m: f"{m.group(1)}=<REDACTED>", text)
    return text


class SecretStore:
    """Stores secret *values* keyed by scoped ref; exposes only refs.

    The value is held privately and is never returned as part of a
    :class:`~aios.security.context.SecurityContext`. Use :meth:`redact` to scrub
    secret values from log records / messages before they are emitted.
    """

    def __init__(self) -> None:
        self._secrets: Dict[str, SecretRef] = {}

    def put(
        self, ref_id: str, value: str, scope: str = "default", kind: str = "generic"
    ) -> SecretRef:
        ref = SecretRef(ref_id=ref_id, scope=scope, kind=kind)
        ref._value = value
        self._secrets[ref_id] = ref
        return ref

    def get_ref(self, ref_id: str) -> Optional[SecretRef]:
        ref = self._secrets.get(ref_id)
        if ref is None:
            return None
        # Return a copy WITHOUT the value.
        return SecretRef(ref_id=ref.ref_id, scope=ref.scope, kind=ref.kind)

    def resolve(self, ref_id: str) -> str:
        ref = self._secrets.get(ref_id)
        if ref is None:
            raise SecretError(f"unknown secret ref: {ref_id}")
        return ref._value

    def redact(self, text: str) -> str:
        """Scrub known secret values and ``key=value`` patterns from ``text``."""
        if not isinstance(text, str):
            text = str(text)
        # 1) redact any known secret values stored in this store.
        for ref in self._secrets.values():
            val = ref._value
            if val and val in text:
                text = text.replace(val, "<REDACTED>")
        # 2) redact generic key=value secret patterns.
        text = redact_message(text)
        return text

    def redact_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Return a copy of ``record`` with string values redacted."""
        return {
            k: (self.redact(v) if isinstance(v, str) else v)
            for k, v in record.items()
        }
