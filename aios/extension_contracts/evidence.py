"""Extension error + evidence helpers."""

from __future__ import annotations

from aios.extension_contracts.contracts import ExtensionError, ExtensionEvidence


def make_error(code: str, message: str, extension_id: str) -> ExtensionError:
    return ExtensionError(code=code, message=message, extension_id=extension_id)


def make_evidence(extension_id: str, action: str, provenance: list[str]) -> ExtensionEvidence:
    return ExtensionEvidence(extension_id=extension_id, action=action, provenance=provenance)
