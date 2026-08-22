"""SkillDistiller + Static Deploy (TASK-083, M11).

* ``DistilledSkill`` — a skill distilled from a workflow/behavior, conforming
  to the public contract 1.0 (T064).
* ``SkillDistiller`` — deterministic distillation (same workflow + distiller ->
  same skill). Produces a contract with inputs/outputs schema.
* ``StaticPackage`` — self-contained package (no dynamic runtime dependency).
* ``StaticDeploy`` — installs the skill and verifies architecture conformance
  via the guard (T063); fail-closed on contract/guard violations.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from aios.governance.architecture.guard import scan_source


class DistillerError(Exception):
    """Raised on skill distillation / deploy contract violations (fail-closed)."""


CONTRACT_VERSION = "1.0.0"
# Modules that would imply a dynamic runtime dependency (not allowed in static pkg).
_DYNAMIC_IMPORTS = ("subprocess", "os", "importlib", "eval", "exec")


@dataclass
class DistilledSkill:
    """A skill distilled from a workflow, conforming to contract 1.0."""

    skill_id: str
    contract_version: str
    inputs_schema: dict[str, Any]
    outputs_schema: dict[str, Any]
    static_package_ref: str
    conforms_to: str
    evidence_ref: str = ""
    source_workflow: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "contract_version": self.contract_version,
            "inputs_schema": self.inputs_schema,
            "outputs_schema": self.outputs_schema,
            "static_package_ref": self.static_package_ref,
            "conforms_to": self.conforms_to,
            "evidence_ref": self.evidence_ref,
            "source_workflow": self.source_workflow,
        }


class SkillDistiller:
    """Deterministically distills a workflow/behavior into a DistilledSkill."""

    def distill(
        self,
        workflow: dict[str, Any],
        skill_id: str,
        static_package_ref: str = "",
        evidence_ref: str = "",
    ) -> DistilledSkill:
        """Distill a workflow definition into a contract-conformant skill."""
        if not skill_id:
            raise DistillerError("skill_id required")
        inputs_schema = dict(workflow.get("inputs", {}))
        outputs_schema = dict(workflow.get("outputs", {}))
        # Deterministic: stable serialization of the distilled contract.
        digest = hashlib.sha256(
            json.dumps(
                {"skill_id": skill_id, "inputs": inputs_schema, "outputs": outputs_schema},
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        return DistilledSkill(
            skill_id=skill_id,
            contract_version=CONTRACT_VERSION,
            inputs_schema=inputs_schema,
            outputs_schema=outputs_schema,
            static_package_ref=static_package_ref or f"pkg-{digest[:8]}",
            conforms_to="architecture(1.0)",
            evidence_ref=evidence_ref,
            source_workflow=workflow.get("name", ""),
        )

    def conforms(self, skill: DistilledSkill) -> bool:
        return skill.contract_version == CONTRACT_VERSION


class StaticPackage:
    """A self-contained package with no dynamic runtime dependency."""

    def __init__(self, package_id: str, source_code: str = "") -> None:
        self.package_id = package_id
        self.source_code = source_code

    def has_dynamic_dependency(self) -> bool:
        """True if the package imports a dynamic-runtime primitive."""
        for dyn in _DYNAMIC_IMPORTS:
            if f"import {dyn}" in self.source_code or f"from {dyn} " in self.source_code:
                return True
        return False

    def is_self_contained(self) -> bool:
        return not self.has_dynamic_dependency()


class StaticDeploy:
    """Deploys a static package after contract + architecture conformance."""

    def __init__(self, distiller: Optional[SkillDistiller] = None) -> None:
        self._distiller = distiller or SkillDistiller()

    def deploy(self, skill: DistilledSkill, package: StaticPackage) -> dict[str, Any]:
        """Install a skill; fail-closed on contract/guard violations."""
        if not self._distiller.conforms(skill):
            raise DistillerError(
                f"skill {skill.skill_id} does not conform to contract 1.0 (T064)"
            )
        if not package.is_self_contained():
            raise DistillerError("static package has dynamic runtime dependency (blocked)")
        # Architecture conformance via guard (T063).
        violations = scan_source(package.source_code, module_path=f"skill/{skill.skill_id}.py")
        if violations:
            rules = ", ".join(sorted({v.rule for v in violations}))
            raise DistillerError(f"static deploy violates architecture guard: {rules} (T063)")
        return {
            "skill_id": skill.skill_id,
            "deployed": True,
            "static_package_ref": skill.static_package_ref,
            "conforms_to": skill.conforms_to,
        }
