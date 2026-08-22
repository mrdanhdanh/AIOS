"""Extension validator."""
from __future__ import annotations

from aios.extension_contracts.compatibility import is_compatible
from aios.extension_contracts.contracts import ExtensionSpec, CapabilityExport

# Internal (non-public) modules an extension must NOT import directly.
_INTERNAL_BOUNDARY = ("aios.runtime.", "aios.core.", "aios.governance.")


class ExtensionValidator:
    def validate_spec(self, spec: ExtensionSpec) -> dict:
        errors = []
        if not spec.name: errors.append("Name required")
        if not spec.version: errors.append("Version required")
        if not is_compatible(spec.version, "1.0.0"):
            errors.append("Spec version incompatible with public contract 1.0.0")
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_capability(self, cap: CapabilityExport) -> dict:
        errors = []
        if not cap.name: errors.append("Capability name required")
        return {"valid": len(errors) == 0, "errors": errors}

    def check_boundary(self, spec: ExtensionSpec, imported_modules: list[str]) -> dict:
        """Fail-closed: reject imports of internal (non-public) modules."""
        violations = [m for m in imported_modules if m.startswith(_INTERNAL_BOUNDARY)]
        return {"valid": len(violations) == 0, "violations": violations}
