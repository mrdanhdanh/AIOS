"""Architecture rule engine — ARCH-A..H + INV-001..010 (TASK-016).

Maps invariants to enforceable rules, defines allowed/forbidden matrices,
and evaluates scan results + dependency graph to produce violations.

Layering: governance — stdlib + aios.core only, no runtime/agent imports.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .guard import (
    AGENT_FORBIDDEN,
    ALLOWED_IMPORT_LAYERS,
    LAYER_KEYWORDS,
    LAYER_ORDER,
    SKILL_FORBIDDEN,
    WORKER_FORBIDDEN,
    classify_module,
)
from .violations import ArchitectureViolation, Severity, ViolationStatus, ViolationType, create_violation


# ---------------------------------------------------------------------------
# Invariants INV-001..010 (canonical definitions per T016 §4)
# ---------------------------------------------------------------------------
INVARIANTS: Dict[str, Dict[str, str]] = {
    "INV-001": {"description": "Orchestrator không trở thành God Object", "category": "ARCH-G"},
    "INV-002": {"description": "Agent không truy cập Tool trực tiếp", "category": "ARCH-B"},
    "INV-003": {"description": "Workflow không phụ thuộc implementation của Engine", "category": "ARCH-C"},
    "INV-004": {"description": "Execution không bypass Policy", "category": "ARCH-F"},
    "INV-005": {"description": "Capability là boundary giữa Agent và Tool", "category": "ARCH-E"},
    "INV-006": {"description": "Runtime Service chỉ truy cập qua contract", "category": "ARCH-E"},
    "INV-007": {"description": "Dependency phải theo layer direction", "category": "ARCH-A"},
    "INV-008": {"description": "Không tạo circular dependency", "category": "ARCH-D"},
    "INV-009": {"description": "LLM không bypass deterministic control path", "category": "ARCH-G"},
    "INV-010": {"description": "Plugin/Skill không bypass Core/Runtime boundary", "category": "ARCH-H"},
}


# ---------------------------------------------------------------------------
# Rule definitions — ARCH-A..H categories + ARCH-001..004 legacy
# ---------------------------------------------------------------------------
@dataclass
class ArchitectureRule:
    rule_id: str
    category: str  # ARCH-A..H
    invariant_id: Optional[str]
    description: str
    severity: str = Severity.ERROR.value
    source_layer: Optional[str] = None
    target_layer: Optional[str] = None
    allowed: bool = False  # True=allowed, False=denied
    evidence: str = ""


# Canonical rule set covering INV-001..010 and ARCH-A..H
RULES: List[ArchitectureRule] = [
    # ARCH-A — Import Boundary
    ArchitectureRule("ARCH-001", "ARCH-A", "INV-002", "Agent must not import execution primitives (subprocess/os) directly.", Severity.ERROR.value, "agent", "tool", False),
    ArchitectureRule("ARCH-002", "ARCH-A", "INV-002", "Agent must not import provider adapters directly.", Severity.ERROR.value, "agent", "tool", False),
    ArchitectureRule("ARCH-003", "ARCH-A", "INV-002", "Agent must not import filesystem adapters directly.", Severity.ERROR.value, "agent", "tool", False),
    ArchitectureRule("ARCH-004", "ARCH-A", "INV-007", "Imports must respect layering Agent->Orchestrator->Worker->Runtime->Skill->Capability->Tool.", Severity.ERROR.value, None, None, False),
    # ARCH-B — Forbidden Dependency
    ArchitectureRule("ARCH-B-001", "ARCH-B", "INV-002", "Agent/Worker forbidden dependencies (subprocess, docker, requests, provider SDK, filesystem impl).", Severity.ERROR.value, "agent", None, False),
    ArchitectureRule("ARCH-B-002", "ARCH-B", "INV-002", "Worker forbidden dependencies (same as agent plus runtime internals).", Severity.ERROR.value, "worker", None, False),
    # ARCH-C — Reverse Dependency
    ArchitectureRule("ARCH-C-001", "ARCH-C", "INV-007", "Reverse dependency forbidden (Tool->Agent, Runtime->Orchestrator, Capability->Agent, Workflow Engine->Domain).", Severity.ERROR.value, None, None, False),
    # ARCH-D — Circular Dependency
    ArchitectureRule("ARCH-D-001", "ARCH-D", "INV-008", "Circular dependency forbidden (A->B->C->A).", Severity.ERROR.value, None, None, False),
    # ARCH-E — Contract Boundary
    ArchitectureRule("ARCH-E-001", "ARCH-E", "INV-005", "Agent must access Tool via Capability contract, not concrete Tool implementation.", Severity.ERROR.value, "agent", "tool", False),
    ArchitectureRule("ARCH-E-002", "ARCH-E", "INV-006", "Runtime Service must be accessed via contract, not implementation.", Severity.ERROR.value, None, None, False),
    ArchitectureRule("ARCH-E-003", "ARCH-E", "INV-005", "Worker must access Tool via Capability contract.", Severity.ERROR.value, "worker", "tool", False),
    # ARCH-F — Policy Bypass
    ArchitectureRule("ARCH-F-001", "ARCH-F", "INV-004", "Execution must not bypass Policy/Permission (Policy->Permission->Execution).", Severity.ERROR.value, None, None, False),
    # ARCH-G — Deterministic Path + Orchestrator God Object
    ArchitectureRule("ARCH-G-001", "ARCH-G", "INV-009", "LLM must not bypass deterministic control path (only when INSUFFICIENT).", Severity.ERROR.value, None, None, False),
    ArchitectureRule("ARCH-G-002", "ARCH-G", "INV-001", "Orchestrator must not become God Object (no direct Tool/Provider/Storage/Sandbox/Scheduler/Persistence impl).", Severity.ERROR.value, "orchestrator", None, False),
    # ARCH-H — Plugin Isolation + Workflow Engine
    ArchitectureRule("ARCH-H-001", "ARCH-H", "INV-010", "Skill/plugin must not bypass Core/Runtime boundary (no private Core, no Runtime internals).", Severity.ERROR.value, "skill", None, False),
    ArchitectureRule("ARCH-H-002", "ARCH-H", "INV-003", "Workflow Definition must not depend directly on engine implementation (langgraph).", Severity.ERROR.value, "runtime", "tool", False),
]

RULE_BY_ID: Dict[str, ArchitectureRule] = {r.rule_id: r for r in RULES}
# Also index legacy ARCH-001..004
for r in RULES:
    if r.rule_id.startswith("ARCH-00"):
        RULE_BY_ID[r.rule_id] = r


# ---------------------------------------------------------------------------
# Forbidden matrices for specialized checks
# ---------------------------------------------------------------------------
# Orchestrator God Object — forbidden direct imports (INV-001)
ORCHESTRATOR_FORBIDDEN = {
    "aios.tool.adapters": "ARCH-G-002",
    "aios.tool.registry": "ARCH-G-002",
    "aios.runtime.providers": "ARCH-G-002",
    "aios.runtime.memory": "ARCH-G-002",
    "aios.skill.sandbox": "ARCH-G-002",
    "aios.runtime.scheduler": "ARCH-G-002",
    "aios.runtime.state": "ARCH-G-002",
    "aios.runtime.artifact": "ARCH-G-002",
    "subprocess": "ARCH-G-002",
    "docker": "ARCH-G-002",
}

# Workflow engine coupling — forbidden imports in workflow domain (INV-003)
WORKFLOW_FORBIDDEN = {
    "langgraph": "ARCH-H-002",
    "langgraph.graph": "ARCH-H-002",
    "langgraph.prebuilt": "ARCH-H-002",
    "langgraph.internal": "ARCH-H-002",
    "jinja2": "ARCH-H-002",
}

# Capability boundary — Agent/Worker must not import concrete Tool (INV-005)
CAPABILITY_FORBIDDEN = {
    "aios.tool": "ARCH-E-001",
    "aios.tool.adapters": "ARCH-E-001",
    "aios.tool.registry": "ARCH-E-001",
    "tool": "ARCH-E-001",
}

# Policy bypass — execution without policy (INV-004)
# Checked via call graph: Agent->Tool.execute without Policy
POLICY_BYPASS_PATTERNS = [
    "Tool.execute",
    "PythonTool",
    "ShellTool",
    "DockerTool",
]

# Plugin isolation — Skill must not import Core private or Runtime internals (INV-010)
# SKILL_FORBIDDEN already covers most; add Core private
SKILL_CORE_FORBIDDEN = {
    "aios.core.container": "ARCH-H-001",
    "aios.core.events": "ARCH-H-001",
    "aios.governance": "ARCH-H-001",
    "aios.runtime.kernel": "ARCH-H-001",
    "aios.runtime.execution": "ARCH-H-001",
    "aios.runtime.policy": "ARCH-H-001",
    "aios.runtime.permission": "ARCH-H-001",
    "aios.runtime.state": "ARCH-H-001",
    "aios.runtime.artifact": "ARCH-H-001",
}

# Contract boundary — Runtime via contract only (INV-006)
# Runtime should not import agent/orchestrator
RUNTIME_FORBIDDEN = {
    "aios.agents": "ARCH-E-002",
    "aios.orchestrator": "ARCH-E-002",
    "aios.agent": "ARCH-E-002",
}


# ---------------------------------------------------------------------------
# Rule evaluation helpers
# ---------------------------------------------------------------------------
def _is_forbidden_import(target: str, forbidden: Dict[str, str]) -> Optional[str]:
    """Check if target matches forbidden dict (exact or prefix). Returns rule_id or None."""
    for forb, rule in forbidden.items():
        if target == forb or target.startswith(forb + "."):
            return rule
    return None


def check_import_boundary(scan_result) -> List[ArchitectureViolation]:
    """ARCH-A: Import boundary — layer violation via ALLOWED_IMPORT_LAYERS."""
    violations: List[ArchitectureViolation] = []
    layer = scan_result.layer
    if layer not in LAYER_ORDER:
        return violations
    allowed = ALLOWED_IMPORT_LAYERS.get(layer, [])
    for imp in scan_result.imports:
        if imp.name == "<dynamic>":
            # Dynamic import with unknown target -> UNKNOWN, fail-closed
            violations.append(create_violation(
                rule_id="ARCH-004",
                invariant_id="INV-007",
                file=scan_result.file,
                line=imp.line,
                source_component=layer,
                target_component="unknown",
                violation_type=ViolationType.IMPORT_BOUNDARY.value,
                severity=Severity.ERROR.value,
                message=f"Dynamic import in layer '{layer}' cannot be verified (UNKNOWN -> FAIL).",
                evidence=f"dynamic import at line {imp.line}",
                status=ViolationStatus.FAIL.value,
            ))
            continue
        target_layer = classify_module(imp.name)
        if target_layer in LAYER_ORDER and target_layer not in allowed:
            violations.append(create_violation(
                rule_id="ARCH-004",
                invariant_id="INV-007",
                file=scan_result.file,
                line=imp.line,
                source_component=layer,
                target_component=target_layer,
                violation_type=ViolationType.LAYER_VIOLATION.value,
                severity=Severity.ERROR.value,
                message=f"Layer '{layer}' imports '{target_layer}' module '{imp.name}' (upward/skip import).",
                evidence=f"import '{imp.name}' at line {imp.line}",
                status=ViolationStatus.FAIL.value,
            ))
    return violations


def check_forbidden_dependency(scan_result) -> List[ArchitectureViolation]:
    """ARCH-B: Forbidden dependency per layer."""
    violations: List[ArchitectureViolation] = []
    layer = scan_result.layer
    forbidden_map = None
    if layer == "agent":
        forbidden_map = AGENT_FORBIDDEN
    elif layer == "worker":
        forbidden_map = WORKER_FORBIDDEN
    elif layer == "skill":
        forbidden_map = SKILL_FORBIDDEN
    else:
        return violations

    for imp in scan_result.imports:
        if imp.name == "<dynamic>":
            continue
        rule = _is_forbidden_import(imp.name, forbidden_map)
        if rule:
            inv = "INV-002" if layer in ("agent", "worker") else "INV-010"
            violations.append(create_violation(
                rule_id=rule,
                invariant_id=inv,
                file=scan_result.file,
                line=imp.line,
                source_component=layer,
                target_component=imp.name,
                violation_type=ViolationType.FORBIDDEN_DEPENDENCY.value,
                severity=Severity.ERROR.value,
                message=f"Layer '{layer}' imports forbidden '{imp.name}' directly.",
                evidence=f"import '{imp.name}' at line {imp.line}",
                status=ViolationStatus.FAIL.value,
            ))
    return violations


def check_reverse_dependency(graph) -> List[ArchitectureViolation]:
    """ARCH-C: Reverse dependency via graph."""
    violations: List[ArchitectureViolation] = []
    reverse = graph.find_reverse_dependencies()
    for src, dst, reason in reverse:
        violations.append(create_violation(
            rule_id="ARCH-C-001",
            invariant_id="INV-007",
            file=src,
            source_component=classify_module(src),
            target_component=classify_module(dst),
            violation_type=ViolationType.REVERSE_DEPENDENCY.value,
            severity=Severity.ERROR.value,
            message=f"Reverse dependency: '{src}' -> '{dst}' ({reason}).",
            evidence=f"edge {src} -> {dst}",
            status=ViolationStatus.FAIL.value,
        ))
    return violations


def check_circular_dependency(graph) -> List[ArchitectureViolation]:
    """ARCH-D: Circular dependency via graph."""
    violations: List[ArchitectureViolation] = []
    cycle = graph.detect_cycle()
    if cycle:
        violations.append(create_violation(
            rule_id="ARCH-D-001",
            invariant_id="INV-008",
            file=" -> ".join(cycle),
            source_component=cycle[0] if cycle else "",
            target_component=cycle[-1] if cycle else "",
            violation_type=ViolationType.CIRCULAR_DEPENDENCY.value,
            severity=Severity.ERROR.value,
            message=f"Circular dependency detected: {' -> '.join(cycle)}",
            evidence=f"cycle: {' -> '.join(cycle)}",
            status=ViolationStatus.FAIL.value,
        ))
    return violations


def check_contract_boundary(scan_result) -> List[ArchitectureViolation]:
    """ARCH-E: Contract boundary — Agent/Worker must not import concrete Tool, Runtime must not import Agent."""
    violations: List[ArchitectureViolation] = []
    layer = scan_result.layer
    # Agent/Worker -> Tool concrete
    if layer in ("agent", "worker"):
        for imp in scan_result.imports:
            if imp.name == "<dynamic>":
                continue
            rule = _is_forbidden_import(imp.name, CAPABILITY_FORBIDDEN)
            if rule:
                # But allow capability contract itself
                if "capability" in imp.name.lower():
                    continue
                violations.append(create_violation(
                    rule_id=rule,
                    invariant_id="INV-005",
                    file=scan_result.file,
                    line=imp.line,
                    source_component=layer,
                    target_component=imp.name,
                    violation_type=ViolationType.CONTRACT_BOUNDARY.value,
                    severity=Severity.ERROR.value,
                    message=f"Layer '{layer}' imports concrete Tool '{imp.name}' instead of Capability contract.",
                    evidence=f"import '{imp.name}' at line {imp.line}",
                    status=ViolationStatus.FAIL.value,
                ))
        # Also check calls: direct Tool instantiation
        for call in scan_result.calls:
            if any(tool in call.func for tool in ["PythonTool", "ShellTool", "DockerTool", "GitTool", "RestTool", "McpTool"]):
                violations.append(create_violation(
                    rule_id="ARCH-E-001",
                    invariant_id="INV-005",
                    file=scan_result.file,
                    line=call.line,
                    source_component=layer,
                    target_component=call.func,
                    violation_type=ViolationType.CONTRACT_BOUNDARY.value,
                    severity=Severity.ERROR.value,
                    message=f"Layer '{layer}' directly instantiates/calls Tool '{call.func}' instead of via Capability.",
                    evidence=f"call '{call.func}' at line {call.line}",
                    status=ViolationStatus.FAIL.value,
                ))
    # Runtime -> Agent/Orchestrator
    if layer == "runtime":
        for imp in scan_result.imports:
            if imp.name == "<dynamic>":
                continue
            rule = _is_forbidden_import(imp.name, RUNTIME_FORBIDDEN)
            if rule:
                violations.append(create_violation(
                    rule_id=rule,
                    invariant_id="INV-006",
                    file=scan_result.file,
                    line=imp.line,
                    source_component=layer,
                    target_component=imp.name,
                    violation_type=ViolationType.CONTRACT_BOUNDARY.value,
                    severity=Severity.ERROR.value,
                    message=f"Runtime imports '{imp.name}' (should only via contract).",
                    evidence=f"import '{imp.name}' at line {imp.line}",
                    status=ViolationStatus.FAIL.value,
                ))
    # Capability should not import runtime/agent
    if layer == "capability":
        for imp in scan_result.imports:
            if imp.name.startswith("aios.runtime") or imp.name.startswith("aios.agents") or imp.name.startswith("aios.orchestrator"):
                violations.append(create_violation(
                    rule_id="ARCH-E-002",
                    invariant_id="INV-006",
                    file=scan_result.file,
                    line=imp.line,
                    source_component=layer,
                    target_component=imp.name,
                    violation_type=ViolationType.CONTRACT_BOUNDARY.value,
                    severity=Severity.ERROR.value,
                    message=f"Capability imports '{imp.name}' (should be pure abstraction).",
                    evidence=f"import '{imp.name}' at line {imp.line}",
                    status=ViolationStatus.FAIL.value,
                ))
    return violations


def check_policy_bypass(scan_result) -> List[ArchitectureViolation]:
    """ARCH-F: Policy bypass — Agent/Worker directly calling Tool without Policy."""
    violations: List[ArchitectureViolation] = []
    layer = scan_result.layer
    if layer in ("agent", "worker", "skill"):
        # If layer imports tool and also has execute calls without policy import, flag
        has_tool_import = any("tool" in imp.name.lower() or "Tool" in imp.name for imp in scan_result.imports)
        has_policy_import = any("policy" in imp.name.lower() or "permission" in imp.name.lower() for imp in scan_result.imports)
        has_execute_call = any("execute" in call.func.lower() or "Tool" in call.func for call in scan_result.calls)
        if has_tool_import and has_execute_call and not has_policy_import:
            # Check if any call is Tool execution
            for call in scan_result.calls:
                if "execute" in call.func.lower() or any(t in call.func for t in ["PythonTool", "ShellTool", "DockerTool"]):
                    violations.append(create_violation(
                        rule_id="ARCH-F-001",
                        invariant_id="INV-004",
                        file=scan_result.file,
                        line=call.line,
                        source_component=layer,
                        target_component=call.func,
                        violation_type=ViolationType.POLICY_BYPASS.value,
                        severity=Severity.ERROR.value,
                        message=f"Layer '{layer}' executes '{call.func}' without Policy/Permission check (bypass).",
                        evidence=f"call '{call.func}' at line {call.line} without policy import",
                        status=ViolationStatus.FAIL.value,
                    ))
                    break
    # Runtime execution must import policy
    if layer == "runtime" and "execution" in scan_result.file.lower():
        has_policy = any("policy" in imp.name.lower() for imp in scan_result.imports)
        if not has_policy:
            # Check if file is execution.py and should have policy
            if "execution.py" in scan_result.file:
                violations.append(create_violation(
                    rule_id="ARCH-F-001",
                    invariant_id="INV-004",
                    file=scan_result.file,
                    source_component=layer,
                    target_component="policy",
                    violation_type=ViolationType.POLICY_BYPASS.value,
                    severity=Severity.ERROR.value,
                    message="Execution module does not import Policy (bypass).",
                    evidence="missing policy import in execution.py",
                    status=ViolationStatus.FAIL.value,
                ))
    return violations


def check_orchestrator_boundary(scan_result) -> List[ArchitectureViolation]:
    """ARCH-G-002: Orchestrator God Object — forbidden direct ownership."""
    violations: List[ArchitectureViolation] = []
    if scan_result.layer != "orchestrator":
        return violations
    for imp in scan_result.imports:
        if imp.name == "<dynamic>":
            continue
        rule = _is_forbidden_import(imp.name, ORCHESTRATOR_FORBIDDEN)
        if rule:
            violations.append(create_violation(
                rule_id=rule,
                invariant_id="INV-001",
                file=scan_result.file,
                line=imp.line,
                source_component="orchestrator",
                target_component=imp.name,
                violation_type=ViolationType.ORCHESTRATOR_GOD_OBJECT.value,
                severity=Severity.ERROR.value,
                message=f"Orchestrator imports forbidden '{imp.name}' directly (God Object).",
                evidence=f"import '{imp.name}' at line {imp.line}",
                status=ViolationStatus.FAIL.value,
            ))
    # Also check for large file heuristic: if orchestrator file has >500 lines and many imports, flag
    # (We don't have line count here, but we can check number of imports as proxy)
    if len(scan_result.imports) > 20:
        violations.append(create_violation(
            rule_id="ARCH-G-002",
            invariant_id="INV-001",
            file=scan_result.file,
            source_component="orchestrator",
            target_component="fan-out",
            violation_type=ViolationType.ORCHESTRATOR_GOD_OBJECT.value,
            severity=Severity.WARNING.value,
            message=f"Orchestrator module '{scan_result.file}' has high fan-out ({len(scan_result.imports)} imports) — potential God Object.",
            evidence=f"{len(scan_result.imports)} imports",
            status=ViolationStatus.FAIL.value,
        ))
    return violations


def check_workflow_engine(scan_result) -> List[ArchitectureViolation]:
    """ARCH-H-002: Workflow engine independence."""
    violations: List[ArchitectureViolation] = []
    # Check if file is workflow domain (definition, validation) and imports langgraph
    is_workflow_domain = "workflow" in scan_result.file.lower() and any(x in scan_result.file.lower() for x in ["definition", "validation", "workflow"])
    # Also check any file that is workflow layer but not compiler
    is_compiler = "compiler" in scan_result.file.lower()
    if is_workflow_domain and not is_compiler:
        for imp in scan_result.imports:
            if imp.name == "<dynamic>":
                continue
            rule = _is_forbidden_import(imp.name, WORKFLOW_FORBIDDEN)
            if rule:
                violations.append(create_violation(
                    rule_id=rule,
                    invariant_id="INV-003",
                    file=scan_result.file,
                    line=imp.line,
                    source_component=scan_result.layer,
                    target_component=imp.name,
                    violation_type=ViolationType.CONTRACT_BOUNDARY.value,
                    severity=Severity.ERROR.value,
                    message=f"Workflow domain '{scan_result.file}' imports engine '{imp.name}' directly (coupling).",
                    evidence=f"import '{imp.name}' at line {imp.line}",
                    status=ViolationStatus.FAIL.value,
                ))
    # Also check any workflow file that is not compiler but imports langgraph
    if "workflow" in scan_result.module_path.lower() and not is_compiler:
        for imp in scan_result.imports:
            if "langgraph" in imp.name.lower():
                violations.append(create_violation(
                    rule_id="ARCH-H-002",
                    invariant_id="INV-003",
                    file=scan_result.file,
                    line=imp.line,
                    source_component=scan_result.layer,
                    target_component=imp.name,
                    violation_type=ViolationType.CONTRACT_BOUNDARY.value,
                    severity=Severity.ERROR.value,
                    message=f"Workflow module '{scan_result.file}' imports langgraph directly.",
                    evidence=f"import '{imp.name}' at line {imp.line}",
                    status=ViolationStatus.FAIL.value,
                ))
                break
    return violations


def check_plugin_isolation(scan_result) -> List[ArchitectureViolation]:
    """ARCH-H-001: Plugin isolation — Skill must not bypass Core/Runtime."""
    violations: List[ArchitectureViolation] = []
    if scan_result.layer != "skill":
        return violations
    for imp in scan_result.imports:
        if imp.name == "<dynamic>":
            continue
        # Check SKILL_FORBIDDEN already covers some, but also check Core private
        rule = _is_forbidden_import(imp.name, SKILL_CORE_FORBIDDEN)
        if rule:
            violations.append(create_violation(
                rule_id=rule,
                invariant_id="INV-010",
                file=scan_result.file,
                line=imp.line,
                source_component="skill",
                target_component=imp.name,
                violation_type=ViolationType.PLUGIN_ISOLATION.value,
                severity=Severity.ERROR.value,
                message=f"Skill imports forbidden Core/Runtime '{imp.name}' (isolation bypass).",
                evidence=f"import '{imp.name}' at line {imp.line}",
                status=ViolationStatus.FAIL.value,
            ))
        # Also check for direct Core private imports (e.g., aios.core.* private).
        # Skill may only use the public Core contracts/version (and their
        # submodules); config/logging shared utilities are also permitted.
        # Prefix matching covers submodule imports like aios.core.contracts.Contract.
        if imp.name.startswith("aios.core."):
            allowed_core = (
                imp.name == "aios.core.version"
                or imp.name.startswith("aios.core.version.")
                or imp.name == "aios.core.contracts"
                or imp.name.startswith("aios.core.contracts.")
                or imp.name == "aios.core.config"
                or imp.name.startswith("aios.core.config.")
                or imp.name == "aios.core.logging"
                or imp.name.startswith("aios.core.logging.")
            )
            if not allowed_core:
                violations.append(create_violation(
                    rule_id="ARCH-H-001",
                    invariant_id="INV-010",
                    file=scan_result.file,
                    line=imp.line,
                    source_component="skill",
                    target_component=imp.name,
                    violation_type=ViolationType.PLUGIN_ISOLATION.value,
                    severity=Severity.ERROR.value,
                    message=f"Skill imports Core private '{imp.name}' (should use public contract).",
                    evidence=f"import '{imp.name}' at line {imp.line}",
                    status=ViolationStatus.FAIL.value,
                ))
    # Check for direct runtime mutation via calls (e.g., modifying RuntimeKernel)
    for call in scan_result.calls:
        if any(x in call.func for x in ["RuntimeKernel", "Container.register", "StateStore", "ArtifactStore"]):
            # Skill should not directly mutate runtime internals
            if "skill" in scan_result.file.lower():
                violations.append(create_violation(
                    rule_id="ARCH-H-001",
                    invariant_id="INV-010",
                    file=scan_result.file,
                    line=call.line,
                    source_component="skill",
                    target_component=call.func,
                    violation_type=ViolationType.PLUGIN_ISOLATION.value,
                    severity=Severity.WARNING.value,
                    message=f"Skill calls '{call.func}' which may mutate Runtime internals.",
                    evidence=f"call '{call.func}' at line {call.line}",
                    status=ViolationStatus.FAIL.value,
                ))
    return violations


def check_deterministic_path(scan_result) -> List[ArchitectureViolation]:
    """ARCH-G-001: Deterministic path — LLM not bypass."""
    violations: List[ArchitectureViolation] = []
    # Check if file is decision_pipeline or planner and has direct LLM call without rule check
    if "decision_pipeline" in scan_result.file.lower() or "planner" in scan_result.file.lower():
        # Look for direct LLM calls (e.g., openai, llm, planner) without RuleEngine check
        has_rule_import = any("rule_engine" in imp.name.lower() or "RuleEngine" in imp.name for imp in scan_result.imports)
        has_llm_call = any("llm" in call.func.lower() or "openai" in call.func.lower() or "planner" in call.func.lower() for call in scan_result.calls)
        # If has LLM call but no rule import, it's bypass
        if has_llm_call and not has_rule_import and "decision_pipeline" in scan_result.file.lower():
            violations.append(create_violation(
                rule_id="ARCH-G-001",
                invariant_id="INV-009",
                file=scan_result.file,
                source_component=scan_result.layer,
                target_component="llm",
                violation_type=ViolationType.DETERMINISTIC_BYPASS.value,
                severity=Severity.ERROR.value,
                message="Decision pipeline calls LLM without deterministic RuleEngine check (bypass).",
                evidence="LLM call without RuleEngine",
                status=ViolationStatus.FAIL.value,
            ))
    # Check for Request -> LLM direct pattern in any orchestrator file
    if scan_result.layer == "orchestrator":
        for call in scan_result.calls:
            if call.func in ("llm", "call_llm", "openai.ChatCompletion", "openai.chat"):
                # Check if file also has normalizer/rule_engine
                has_deterministic = any("normalizer" in imp.name.lower() or "rule_engine" in imp.name.lower() for imp in scan_result.imports)
                if not has_deterministic:
                    violations.append(create_violation(
                        rule_id="ARCH-G-001",
                        invariant_id="INV-009",
                        file=scan_result.file,
                        line=call.line,
                        source_component="orchestrator",
                        target_component=call.func,
                        violation_type=ViolationType.DETERMINISTIC_BYPASS.value,
                        severity=Severity.ERROR.value,
                        message=f"Orchestrator calls LLM '{call.func}' without deterministic path.",
                        evidence=f"call '{call.func}' at line {call.line}",
                        status=ViolationStatus.FAIL.value,
                    ))
    return violations


def evaluate_scan_result(scan_result) -> List[ArchitectureViolation]:
    """Run all rule checks on a single scan result."""
    violations: List[ArchitectureViolation] = []
    # Handle parse error -> UNKNOWN -> FAIL (fail-closed)
    if scan_result.has_parse_error:
        violations.append(create_violation(
            rule_id="ARCH-004",
            invariant_id="INV-007",
            file=scan_result.file,
            source_component=scan_result.layer,
            target_component="parse_error",
            violation_type=ViolationType.IMPORT_BOUNDARY.value,
            severity=Severity.ERROR.value,
            message=f"Parse error in '{scan_result.file}': {scan_result.parse_error} (UNKNOWN -> FAIL).",
            evidence=scan_result.parse_error or "parse error",
            status=ViolationStatus.FAIL.value,
        ))
        return violations

    violations.extend(check_import_boundary(scan_result))
    violations.extend(check_forbidden_dependency(scan_result))
    violations.extend(check_contract_boundary(scan_result))
    violations.extend(check_policy_bypass(scan_result))
    violations.extend(check_orchestrator_boundary(scan_result))
    violations.extend(check_workflow_engine(scan_result))
    violations.extend(check_plugin_isolation(scan_result))
    violations.extend(check_deterministic_path(scan_result))
    return violations


def evaluate_graph(graph) -> List[ArchitectureViolation]:
    """Run graph-level checks (cycle, reverse)."""
    violations: List[ArchitectureViolation] = []
    violations.extend(check_circular_dependency(graph))
    violations.extend(check_reverse_dependency(graph))
    # Also check layer violations via graph
    layer_violations = graph.find_layer_violations()
    for src, dst, reason in layer_violations:
        # Avoid duplicate with import_boundary (which already covers per-file)
        # Only add if not already covered by reverse check
        violations.append(create_violation(
            rule_id="ARCH-004",
            invariant_id="INV-007",
            file=src,
            source_component=classify_module(src),
            target_component=classify_module(dst),
            violation_type=ViolationType.LAYER_VIOLATION.value,
            severity=Severity.ERROR.value,
            message=reason,
            evidence=f"edge {src} -> {dst}",
            status=ViolationStatus.FAIL.value,
        ))
    return violations


__all__ = [
    "INVARIANTS",
    "RULES",
    "RULE_BY_ID",
    "ArchitectureRule",
    "ORCHESTRATOR_FORBIDDEN",
    "WORKFLOW_FORBIDDEN",
    "CAPABILITY_FORBIDDEN",
    "SKILL_CORE_FORBIDDEN",
    "RUNTIME_FORBIDDEN",
    "check_import_boundary",
    "check_forbidden_dependency",
    "check_reverse_dependency",
    "check_circular_dependency",
    "check_contract_boundary",
    "check_policy_bypass",
    "check_orchestrator_boundary",
    "check_workflow_engine",
    "check_plugin_isolation",
    "check_deterministic_path",
    "evaluate_scan_result",
    "evaluate_graph",
]
