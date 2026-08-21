"""Normalizer — Request → NormalizedRequest (TASK-010).

Deterministic, no LLM. Handles alias, command normalization, parameter
normalization, default values, target resolution, mode/priority/metadata.

Layering: orchestrator — may import runtime/capability/tool/unknown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["NormalizedRequest", "Normalizer", "NormalizerError"]


class NormalizerError(Exception):
    pass


# Alias map: raw lowercased phrase → canonical intent
_ALIASES: Dict[str, str] = {
    "run tests": "run_tests",
    "run test": "run_tests",
    "run_tests": "run_tests",
    "show system health": "health",
    "system health": "health",
    "health check": "health",
    "health": "health",
    "status": "status",
    "help": "help",
    "list tasks": "list_tasks",
    "list task": "list_tasks",
    "list_tasks": "list_tasks",
    "list skills": "list_skills",
    "list skill": "list_skills",
    "list_skills": "list_skills",
    "review code": "review_code",
    "review project": "review_code",
    "review_code": "review_code",
    "diagnose runtime": "diagnose_runtime",
    "diagnose": "diagnose_runtime",
    "diagnose_runtime": "diagnose_runtime",
    "create crud api": "create_crud_api",
    "crud api": "create_crud_api",
    "crud-generator": "create_crud_api",
}

# Priority vocab
_ALLOWED_PRIORITIES = {"critical", "high", "normal", "low"}
_ALLOWED_MODES = {"execute", "plan", "simulate", "validate"}


@dataclass(frozen=True)
class NormalizedRequest:
    """Deterministic normalized representation of a raw request."""

    intent: str
    raw_text: str = ""
    normalized_text: str = ""
    target_type: str = "workspace"
    target_value: str = "current"
    mode: str = "execute"
    priority: str = "normal"
    signals: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_channel: str = "api"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "target": {"type": self.target_type, "value": self.target_value},
            "mode": self.mode,
            "priority": self.priority,
            "signals": dict(self.signals),
            "metadata": dict(self.metadata),
            "source_channel": self.source_channel,
        }


class Normalizer:
    """Stage 1: normalize raw request into typed intent."""

    def normalize(self, request: Any) -> NormalizedRequest:
        # Accept governance Request or any object with .text/.metadata or dict
        if isinstance(request, dict):
            text = str(request.get("text", "") or "")
            metadata = dict(request.get("metadata", {}) or {})
            source_channel = str(request.get("source_channel", "api"))
        else:
            text = str(getattr(request, "text", "") or "")
            metadata = dict(getattr(request, "metadata", {}) or {})
            source_channel = str(getattr(request, "source_channel", metadata.get("source_channel", "api")))

        raw_text = text
        # Basic cleanup: strip, lower, collapse whitespace, remove punctuation except _ -
        cleaned = text.strip()
        lowered = cleaned.lower()
        # Collapse whitespace
        collapsed = re.sub(r"\s+", " ", lowered).strip()
        # Remove trailing punctuation
        collapsed = re.sub(r"[.!?]+$", "", collapsed).strip()

        # Alias lookup: exact match first, then substring
        intent = _ALIASES.get(collapsed)
        if intent is None:
            # Try to find alias as substring or intent as normalized collapsed
            # Replace spaces with underscores for fallback intent
            fallback = re.sub(r"[^a-z0-9_]+", "_", collapsed).strip("_")
            # Check if fallback matches known alias value
            if fallback in set(_ALIASES.values()):
                intent = fallback
            else:
                # Check substring alias
                for alias_phrase, canonical in _ALIASES.items():
                    if alias_phrase in collapsed or collapsed in alias_phrase:
                        intent = canonical
                        break
                if intent is None:
                    intent = fallback or "unknown"

        # Target resolution
        target_type = str(metadata.get("target_type", "workspace"))
        target_value = str(metadata.get("target_value", metadata.get("target", "current")))
        # Heuristic: if raw contains workspace/project/file hint
        if "workspace" in lowered:
            target_type = "workspace"
        elif "file" in lowered:
            # try to extract file hint
            m = re.search(r"file\s+(\S+)", lowered)
            if m:
                target_type = "file"
                target_value = m.group(1)

        # Mode
        mode = str(metadata.get("mode", "execute")).lower()
        if mode not in _ALLOWED_MODES:
            mode = "execute"

        # Priority
        priority = str(metadata.get("priority", "normal")).lower()
        if priority not in _ALLOWED_PRIORITIES:
            priority = "normal"

        # Signals: copy metadata string values
        signals: Dict[str, str] = {}
        for k, v in metadata.items():
            if isinstance(v, str):
                signals[k] = v
            else:
                signals[k] = str(v)

        # Source channel
        if "source_channel" in metadata:
            source_channel = str(metadata["source_channel"])

        return NormalizedRequest(
            intent=intent,
            raw_text=raw_text,
            normalized_text=collapsed,
            target_type=target_type,
            target_value=target_value,
            mode=mode,
            priority=priority,
            signals=signals,
            metadata=dict(metadata),
            source_channel=source_channel,
        )
