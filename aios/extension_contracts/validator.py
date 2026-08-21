"""Extension validator."""
from __future__ import annotations
from aios.extension_contracts.contracts import ExtensionSpec, CapabilityExport

class ExtensionValidator:
    def validate_spec(self, spec: ExtensionSpec) -> dict:
        errors = []
        if not spec.name: errors.append("Name required")
        if not spec.version: errors.append("Version required")
        return {"valid": len(errors) == 0, "errors": errors}
    def validate_capability(self, cap: CapabilityExport) -> dict:
        errors = []
        if not cap.name: errors.append("Capability name required")
        return {"valid": len(errors) == 0, "errors": errors}
