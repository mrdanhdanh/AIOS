"""Architecture Guard — Rule 3 (Agent never bypasses Runtime/Capability/Policy).

Enforced via AST/import scanning. Rules:
  ARCH-001: Agent cannot import subprocess directly
  ARCH-002: Agent cannot import filesystem/os adapter directly
  ARCH-003: Agent cannot import provider directly
  ARCH-004: Workflow cannot depend on Engine implementation
"""
import ast

RULES = {
    "ARCH-001": "Agent cannot import subprocess directly",
    "ARCH-002": "Agent cannot import filesystem/os adapter directly",
    "ARCH-003": "Agent cannot import provider directly",
    "ARCH-004": "Workflow cannot depend on Engine implementation",
}


class ArchitectureViolation:
    def __init__(self, rule_id, detail):
        self.rule_id = rule_id
        self.detail = detail

    def __repr__(self):
        return f"{self.rule_id}: {self.detail}"


def scan_source(source_code, is_agent=True):
    violations = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return violations
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name or ""
                base = name.split(".")[0]
                # ARCH-001: subprocess (any form)
                if base == "subprocess" or name == "subprocess":
                    violations.append(ArchitectureViolation("ARCH-001", f"import {name}"))
                # ARCH-002: os / pathlib / filesystem adapters (any Import form)
                if is_agent and base in ("os", "pathlib"):
                    violations.append(ArchitectureViolation("ARCH-002", f"import {name}"))
                if is_agent and "filesystem" in name:
                    violations.append(ArchitectureViolation("ARCH-002", f"import {name}"))
                # ARCH-004: workflow -> engine (any Import)
                if "workflow" in name and "engine" in name:
                    violations.append(ArchitectureViolation("ARCH-004", f"import {name}"))
                # detect dynamic import via importlib
                if name in ("importlib",):
                    # will be checked via Call below; mark potential
                    pass
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            base = mod.split(".")[0] if mod else ""
            if mod == "subprocess" or base == "subprocess":
                violations.append(ArchitectureViolation("ARCH-001", f"from {mod} import"))
            if is_agent and ("provider" in mod or "providers" in mod):
                violations.append(ArchitectureViolation("ARCH-003", f"from {mod} import"))
            if is_agent and (mod in ("os", "pathlib") or base in ("os", "pathlib")):
                violations.append(ArchitectureViolation("ARCH-002", f"from {mod} import"))
            if is_agent and "filesystem" in mod:
                violations.append(ArchitectureViolation("ARCH-002", f"from {mod} import"))
            # ARCH-004: workflow depending on engine
            if "workflow" in mod and "engine" in mod:
                violations.append(ArchitectureViolation("ARCH-004", f"from {mod} import"))
            if mod in ("workflow", "engine") or base in ("workflow", "engine"):
                # heuristic: cross-import between workflow and engine
                for alias in node.names:
                    if "engine" in alias.name.lower() and "workflow" in mod.lower():
                        violations.append(ArchitectureViolation("ARCH-004", f"from {mod} import {alias.name}"))
                    if "workflow" in alias.name.lower() and "engine" in mod.lower():
                        violations.append(ArchitectureViolation("ARCH-004", f"from {mod} import {alias.name}"))
        elif isinstance(node, ast.Call):
            # detect __import__('subprocess') / importlib.import_module('subprocess'/'os')
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name in ("__import__", "import_module"):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        val = arg.value
                        base = val.split(".")[0]
                        if base == "subprocess":
                            violations.append(ArchitectureViolation("ARCH-001", f"dynamic import {val}"))
                        if is_agent and base in ("os", "pathlib"):
                            violations.append(ArchitectureViolation("ARCH-002", f"dynamic import {val}"))
                        if is_agent and ("provider" in val):
                            violations.append(ArchitectureViolation("ARCH-003", f"dynamic import {val}"))
                        if "workflow" in val and "engine" in val:
                            violations.append(ArchitectureViolation("ARCH-004", f"dynamic import {val}"))
    return violations
