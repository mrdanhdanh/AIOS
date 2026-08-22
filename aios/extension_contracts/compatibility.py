"""Extension compatibility + dependency resolver (semver, fail-closed)."""

from __future__ import annotations

from aios.extension_contracts.contracts import ExtensionSpec


def _parse(version: str) -> tuple[int, int, int]:
    nums = [int(p.split("-")[0]) for p in version.split(".")[:3]]
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def is_compatible(extension_version: str, contract_version: str) -> bool:
    """Compatible if major matches and extension minor >= contract minor."""
    em, emi, _ = _parse(extension_version)
    cm, cmi, _ = _parse(contract_version)
    if em != cm:
        return False
    return emi >= cmi


class ExtensionDependencyResolver:
    """Resolves extension dependencies against a registry of specs."""

    def __init__(self, contract_version: str = "1.0.0") -> None:
        self._contract_version = contract_version

    def resolve(self, spec: ExtensionSpec, registry: dict[str, ExtensionSpec]) -> list[str]:
        """Return ordered dependency ids; raises on missing/incompatible dep."""
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(eid: str) -> None:
            if eid in visited:
                return
            dep = registry.get(eid)
            if dep is None:
                raise ValueError(f"Missing extension dependency: {eid}")
            if not is_compatible(dep.version, self._contract_version):
                raise ValueError(
                    f"Extension {eid} v{dep.version} incompatible with contract {self._contract_version}"
                )
            visited.add(eid)
            for d in getattr(dep, "dependencies", []):
                visit(d)
            ordered.append(eid)

        visit(spec.spec_id)
        return ordered
