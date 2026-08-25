"""Workflow Definition — declarative contract (TASK-008, M1)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

from aios.core.version import SemVer, VersionError

__all__ = [
    "WorkflowError",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowResource",
    "WorkflowDefinition",
    "ALLOWED_NODE_TYPES",
    "ALLOWED_PERMISSIONS",
    "WORKFLOW_CONTRACT_VERSION",
]

WORKFLOW_CONTRACT_VERSION = "1.0.0"
ALLOWED_NODE_TYPES = {"task"}
ALLOWED_PERMISSIONS = {
    "filesystem.read",
    "filesystem.write",
    "process.execute",
    "network.read",
    "network.write",
    "capability:invoke",
    "tool:invoke",
    "memory:read",
    "memory:write",
}
_MEMORY_RE = re.compile(r"^\d+(KB|MB|GB)$")


class WorkflowError(Exception):
    pass


@dataclass(frozen=True)
class WorkflowResource:
    cpu: int = 1
    memory: str = "512MB"

    def validate(self) -> None:
        if not isinstance(self.cpu, int) or self.cpu <= 0:
            raise WorkflowError(f"resources.cpu must be a positive int, got {self.cpu!r}")
        if not isinstance(self.memory, str) or not _MEMORY_RE.match(self.memory):
            raise WorkflowError(f"resources.memory must match <int><KB|MB|GB>, got {self.memory!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {"cpu": self.cpu, "memory": self.memory}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowResource":
        if not isinstance(data, dict):
            raise WorkflowError(f"resources must be a mapping, got {type(data).__name__}")
        cpu = data.get("cpu", 1)
        memory = data.get("memory", "512MB")
        obj = cls(cpu=cpu, memory=memory)
        obj.validate()
        return obj


@dataclass(frozen=True)
class WorkflowNode:
    id: str
    type: str = "task"
    capability: Optional[str] = None
    description: str = ""
    command: Optional[str] = None  # TASK-222: real command to run (optional)
    cwd: Optional[str] = None  # TASK-224: optional per-node working directory

    def validate(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise WorkflowError("node.id must be a non-empty string")
        if self.type not in ALLOWED_NODE_TYPES:
            raise WorkflowError(f"node type {self.type!r} not in allowed {sorted(ALLOWED_NODE_TYPES)}")
        if self.capability is not None and (not isinstance(self.capability, str) or not self.capability.strip()):
            raise WorkflowError("node.capability must be a non-empty string if provided")

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"id": self.id, "type": self.type}
        if self.capability is not None:
            d["capability"] = self.capability
        if self.description:
            d["description"] = self.description
        if self.command is not None:
            d["command"] = self.command
        if self.cwd is not None:
            d["cwd"] = self.cwd
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowNode":
        if not isinstance(data, dict):
            raise WorkflowError(f"node must be a mapping, got {type(data).__name__}")
        nid = data.get("id")
        if nid is None:
            raise WorkflowError("node missing required field 'id'")
        ntype = data.get("type", "task")
        cap = data.get("capability")
        desc = data.get("description", "")
        cmd = data.get("command")
        node_cwd = data.get("cwd")
        for forbidden in ("engine", "langgraph_node", "langgraph", "engine_config"):
            if forbidden in data:
                raise WorkflowError(f"node contains forbidden engine-specific key {forbidden!r}")
        obj = cls(
            id=str(nid), type=str(ntype), capability=cap,
            description=str(desc) if desc else "",
            command=str(cmd) if cmd else None,
            cwd=str(node_cwd) if node_cwd else None,
        )
        obj.validate()
        return obj


@dataclass(frozen=True)
class WorkflowEdge:
    from_id: str
    to_id: str

    def validate(self) -> None:
        if not isinstance(self.from_id, str) or not self.from_id.strip():
            raise WorkflowError("edge 'from' must be a non-empty string")
        if not isinstance(self.to_id, str) or not self.to_id.strip():
            raise WorkflowError("edge 'to' must be a non-empty string")
        if self.from_id == self.to_id:
            raise WorkflowError(f"edge self-loop not allowed: {self.from_id!r} -> {self.to_id!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {"from": self.from_id, "to": self.to_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowEdge":
        if not isinstance(data, dict):
            raise WorkflowError(f"edge must be a mapping, got {type(data).__name__}")
        f = data.get("from")
        t = data.get("to")
        if f is None or t is None:
            raise WorkflowError("edge missing required 'from' or 'to'")
        obj = cls(from_id=str(f), to_id=str(t))
        obj.validate()
        return obj


@dataclass
class WorkflowDefinition:
    name: str
    version: str
    description: str = ""
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    retries: int = 0
    timeout: int = 300
    resources: Optional[WorkflowResource] = None
    permissions: List[str] = field(default_factory=list)
    contract_version: str = WORKFLOW_CONTRACT_VERSION

    def validate(self) -> None:
        from .validation import validate_definition

        validate_definition(self)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "workflow": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "nodes": [n.to_dict() for n in self.nodes],
                "edges": [e.to_dict() for e in self.edges],
                "retries": self.retries,
                "timeout": self.timeout,
            }
        }
        wf = d["workflow"]
        if self.resources is not None:
            wf["resources"] = self.resources.to_dict()
        if self.permissions:
            wf["permissions"] = list(self.permissions)
        return d

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=True)

    @property
    def semver(self) -> SemVer:
        return SemVer.parse(self.version)

    def content_hash(self) -> str:
        canonical = yaml.safe_dump(self.to_dict(), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_artifact(self, *, artifact_id: Optional[str] = None):
        from aios.runtime.artifact import Artifact

        content = self.to_yaml().encode("utf-8")
        return Artifact.create(
            name=self.name,
            content=content,
            content_type="application/yaml",
            version=self.version,
            artifact_id=artifact_id,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowDefinition":
        if not isinstance(data, dict):
            raise WorkflowError(f"workflow data must be a mapping, got {type(data).__name__}")
        wf = data.get("workflow", data) if "workflow" in data else data
        if not isinstance(wf, dict):
            raise WorkflowError("workflow must be a mapping")
        for forbidden in ("engine", "langgraph", "engine_config", "langgraph_node"):
            if forbidden in wf:
                raise WorkflowError(f"workflow contains forbidden engine-specific key {forbidden!r}")
        name = wf.get("name")
        version = wf.get("version")
        if not name or not isinstance(name, str) or not name.strip():
            raise WorkflowError("workflow.name must be a non-empty string")
        if not version or not isinstance(version, str) or not version.strip():
            raise WorkflowError("workflow.version must be a non-empty string")
        try:
            SemVer.parse(str(version))
        except VersionError as exc:
            raise WorkflowError(f"workflow.version invalid SemVer {version!r}: {exc}") from exc
        description = str(wf.get("description", "") or "")
        raw_nodes = wf.get("nodes", [])
        if raw_nodes is None:
            raw_nodes = []
        if not isinstance(raw_nodes, list):
            raise WorkflowError("workflow.nodes must be a list")
        nodes = [WorkflowNode.from_dict(n) for n in raw_nodes]
        raw_edges = wf.get("edges", [])
        if raw_edges is None:
            raw_edges = []
        if not isinstance(raw_edges, list):
            raise WorkflowError("workflow.edges must be a list")
        edges = [WorkflowEdge.from_dict(e) for e in raw_edges]
        retries = wf.get("retries", 0)
        if not isinstance(retries, int):
            raise WorkflowError(f"workflow.retries must be int, got {type(retries).__name__}")
        timeout = wf.get("timeout", 300)
        if not isinstance(timeout, int):
            raise WorkflowError(f"workflow.timeout must be int, got {type(timeout).__name__}")
        resources = None
        if "resources" in wf and wf["resources"] is not None:
            resources = WorkflowResource.from_dict(wf["resources"])
        permissions: List[str] = []
        if "permissions" in wf and wf["permissions"] is not None:
            raw_perms = wf["permissions"]
            if not isinstance(raw_perms, list):
                raise WorkflowError("workflow.permissions must be a list")
            for p in raw_perms:
                if not isinstance(p, str):
                    raise WorkflowError(f"permission must be string, got {type(p).__name__}")
                if p not in ALLOWED_PERMISSIONS:
                    raise WorkflowError(f"permission {p!r} not allowed")
                permissions.append(p)
        obj = cls(
            name=str(name),
            version=str(version),
            description=description,
            nodes=nodes,
            edges=edges,
            retries=retries,
            timeout=timeout,
            resources=resources,
            permissions=permissions,
        )
        obj.validate()
        return obj

    @classmethod
    def from_yaml(cls, text: str) -> "WorkflowDefinition":
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise WorkflowError(f"invalid YAML: {exc}") from exc
        if data is None or not isinstance(data, dict):
            raise WorkflowError("YAML must contain a mapping with 'workflow' key")
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str) -> "WorkflowDefinition":
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        return cls.from_yaml(text)

    @classmethod
    def from_markdown(cls, text: str) -> "WorkflowDefinition":
        """Parse a simple Markdown plan into a workflow (TASK-222).

        Each line of the form ``- [ ] <command>`` (or ``- [x]``) becomes a node
        whose ``command`` is the text after the checkbox. A leading ``# Title``
        line (if present) becomes the workflow name.
        """
        name = "markdown-plan"
        version = "0.1.0"
        nodes: List["WorkflowNode"] = []
        idx = 0
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith("# ") and name == "markdown-plan":
                name = line[2:].strip() or name
                continue
            if line.startswith("```"):
                continue  # skip fenced code blocks
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                body = line[line.index("]") + 1:].strip()
                if not body:
                    continue
                idx += 1
                nodes.append(
                    WorkflowNode(id=f"step-{idx}", type="task", description=body, command=body)
                )
        if not nodes:
            raise WorkflowError("markdown plan contains no '- [ ]' steps")
        return cls(name=name, version=version, nodes=nodes, permissions=["process.execute"])

    # ------------------------------------------------------------------ #
    # TASK-222 / TASK-228: convert a declarative workflow into a runtime
    # ExecutionPlan (Unified ExecutionPlan Contract, M29).
    # ------------------------------------------------------------------ #
    def to_execution_plan(self, *, allowed_cwd: Optional[str] = None) -> "ExecutionPlan":
        """Build a runtime :class:`~aios.core.planner.ExecutionPlan` for real execution.

        Each node becomes a :class:`~aios.core.planner.Step` carrying the
        ``scope`` / ``resource`` / ``policy_ref`` / ``permission`` metadata
        required by the executor's governance pre-check (PolicyEngine +
        PermissionBroker), plus the real ``command`` to run. This is the
        single, unified contract used by BOTH ``aiagent task`` (Flow A) and
        ``aiagent execute`` (Flow B) — closing the Flow A ∧ Flow B gap.
        """
        from aios.core.planner import ExecutionPlan, Step
        from aios.runtime.permission import PermissionScope

        scope = self._derive_scope()
        plan = ExecutionPlan(plan_id=f"wf-{self.name}-{self.version}")
        plan.metadata["version"] = self.version
        plan.metadata["workflow_name"] = self.name
        plan.metadata["contract"] = "unified-execution-plan"
        plan.metadata["policy_ref"] = "governance.unified-gate"
        plan.metadata["permissions"] = list(self.permissions)
        for node in self.nodes:
            command = node.command or node.description or node.id
            tool_type = "git" if str(command).strip().lower().startswith("git ") else "shell"
            # A node may override its cwd; otherwise fall back to the work dir.
            node_cwd = getattr(node, "cwd", None)
            step_cwd = node_cwd or allowed_cwd
            step = Step(
                step_id=node.id,
                action=str(command),
                metadata={
                    "scope": scope,
                    "resource": node.id,
                    "tool_type": tool_type,
                    "command": str(command),
                    "cwd": step_cwd,
                    "timeout": self.timeout,
                    # TASK-228: explicit unified-contract fields
                    "policy_ref": "governance.unified-gate",
                    "permission": "process.execute" if scope is PermissionScope.EXECUTE else "capability:invoke",
                    "evidence_ref": f"evidence:{node.id}",
                },
            )
            plan.add_step(step)
        return plan

    @classmethod
    def from_execution_plan(cls, plan: "ExecutionPlan") -> "WorkflowDefinition":
        """Round-trip converter (TASK-228): rebuild a declarative workflow.

        Inverse of :meth:`to_execution_plan`. Preserves node id / command /
        description so the conversion is lossless for the fields we control.
        """
        wf_name = plan.metadata.get("workflow_name", "from-execution-plan")
        wf_version = plan.metadata.get("version", "0.1.0")
        nodes = []
        for step in plan.steps:
            meta = step.metadata or {}
            command = meta.get("command", step.action)
            nodes.append(
                WorkflowNode(
                    id=step.step_id,
                    type="task",
                    description=meta.get("description", command),
                    command=command,
                    cwd=meta.get("cwd"),
                )
            )
        permissions = list(plan.metadata.get("permissions", [])) or ["process.execute"]
        return cls(name=wf_name, version=wf_version, nodes=nodes, permissions=permissions)

    def _derive_scope(self) -> "PermissionScope":
        """Map workflow-level permissions to a single step scope (fail-closed EXECUTE)."""
        from aios.runtime.permission import PermissionScope

        perms = set(self.permissions)
        if "process.execute" in perms or "tool:invoke" in perms:
            return PermissionScope.EXECUTE
        if "capability:invoke" in perms:
            return PermissionScope.CAPABILITY_INVOKE
        if "filesystem.write" in perms:
            return PermissionScope.WRITE
        if "filesystem.read" in perms:
            return PermissionScope.READ
        # Default: real command execution requires EXECUTE permission.
        return PermissionScope.EXECUTE
