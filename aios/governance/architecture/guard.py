"""Architecture guard implementation (Rule 3)."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class ArchitectureError(Exception):
    """Raised for unrecoverable scanning errors."""


@dataclass
class Violation:
    rule: str
    module: str
    detail: str
    line: Optional[int] = None


@dataclass
class GateResult:
    passed: bool
    violations: List[Violation] = field(default_factory=list)

    def __bool__(self) -> bool:  # convenient truthiness
        return self.passed


# Layer ordering. Lower index = higher layer (caller); higher index = lower
# layer (callee). Imports must only go "downward".
LAYER_ORDER = ["agent", "orchestrator", "runtime", "capability", "tool"]

# Map a path/module segment (singular or plural) to a layer.
LAYER_KEYWORDS = {
    "agent": "agent",
    "agents": "agent",
    "orchestrator": "orchestrator",
    "orchestrators": "orchestrator",
    "runtime": "runtime",
    "capability": "capability",
    "capabilities": "capability",
    "tool": "tool",
    "tools": "tool",
}


def classify_module(module_path: str) -> str:
    """Classify a module into a layer based on its path. Unknown -> 'unknown'."""
    lowered = module_path.replace("\\", "/").lower()
    for segment in lowered.split("/"):
        if segment in LAYER_KEYWORDS:
            return LAYER_KEYWORDS[segment]
    return "unknown"


# Forbidden direct imports for agent-layer modules (ARCH-001..003).
AGENT_FORBIDDEN = {
    "subprocess": "ARCH-001",
    "os": "ARCH-001",  # os.system / os.popen style execution primitives
    "aios.core.providers": "ARCH-002",
    "aios.runtime.providers": "ARCH-002",
    "providers": "ARCH-002",
    "aios.runtime.filesystem": "ARCH-003",
    "aios.runtime.fs_adapter": "ARCH-003",
    "filesystem": "ARCH-003",
}

# Layer that a given layer is allowed to import (itself and everything below).
ALLOWED_IMPORT_LAYERS: Dict[str, List[str]] = {
    "agent": ["orchestrator", "runtime", "capability", "tool", "unknown"],
    "orchestrator": ["runtime", "capability", "tool", "unknown"],
    "runtime": ["capability", "tool", "unknown"],
    "capability": ["tool", "unknown"],
    "tool": ["unknown"],
    "unknown": LAYER_ORDER + ["unknown"],
}

ARCH_RULES = {
    "ARCH-001": "Agent must not import execution primitives (subprocess/os) directly.",
    "ARCH-002": "Agent must not import provider adapters directly.",
    "ARCH-003": "Agent must not import filesystem adapters directly.",
    "ARCH-004": "Imports must respect layering Agent->Orchestrator->Runtime->Capability->Tool.",
}


def _module_name(node: ast.ImportFrom) -> str:
    return node.module or ""


def scan_source(source_code: str, module_path: str = "<string>") -> List[Violation]:
    """Scan a single source string and return architecture violations."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        raise ArchitectureError(f"Cannot parse {module_path}: {exc}") from exc

    layer = classify_module(module_path)
    violations: List[Violation] = []

    imported_targets: List[Tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_targets.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            mod = _module_name(node)
            # Represent relative imports by their module name if present.
            target = mod if mod else ".".join(n.name for n in node.names)
            imported_targets.append((target, node.lineno))

    for target, lineno in imported_targets:
        # ARCH-001..003: forbidden direct imports for agent layer.
        if layer == "agent":
            for forbidden, rule in AGENT_FORBIDDEN.items():
                if target == forbidden or target.startswith(forbidden + "."):
                    violations.append(
                        Violation(
                            rule=rule,
                            module=module_path,
                            detail=f"Agent imports '{target}' directly (forbidden).",
                            line=lineno,
                        )
                    )
        # ARCH-004: layering. Determine the imported module's layer.
        imported_layer = classify_module(target)
        allowed = ALLOWED_IMPORT_LAYERS.get(layer, LAYER_ORDER)
        if (
            imported_layer in LAYER_ORDER
            and layer in LAYER_ORDER
            and imported_layer not in allowed
        ):
            violations.append(
                Violation(
                    rule="ARCH-004",
                    module=module_path,
                    detail=(
                        f"Layer '{layer}' imports '{imported_layer}' module "
                        f"'{target}' (upward/skip import)."
                    ),
                    line=lineno,
                )
            )
    return violations


class ArchitectureGuard:
    """Runs the architecture gate over source files or directories."""

    def __init__(self, roots: Optional[List[str]] = None) -> None:
        self.roots = roots or []

    def scan_file(self, path: str) -> List[Violation]:
        if not path.endswith(".py"):
            return []
        with open(path, "r", encoding="utf-8") as fh:
            return scan_source(fh.read(), module_path=path)

    def scan_directory(self, directory: str) -> List[Violation]:
        violations: List[Violation] = []
        for root, _dirs, files in os.walk(directory):
            for name in files:
                if name.endswith(".py"):
                    violations.extend(self.scan_file(os.path.join(root, name)))
        return violations

    def check(self, sources: Optional[List[str]] = None) -> GateResult:
        """Check given source strings [(code, module_path)] or self.roots files.

        ``sources`` is a list of ``(code, module_path)`` tuples. If omitted, the
        configured ``roots`` directories are scanned.
        """
        violations: List[Violation] = []
        if sources is not None:
            for code, module_path in sources:
                violations.extend(scan_source(code, module_path))
        else:
            for root in self.roots:
                if os.path.isdir(root):
                    violations.extend(self.scan_directory(root))
                elif os.path.isfile(root):
                    violations.extend(self.scan_file(root))
        return GateResult(passed=len(violations) == 0, violations=violations)
