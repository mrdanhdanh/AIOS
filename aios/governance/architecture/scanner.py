"""AST scanner for architecture enforcement (TASK-016).

Enumerates source files, parses AST, extracts imports, calls, inheritance,
decorators, package ownership, layer classification, and generates
machine-readable scan results.

Layering: governance — stdlib + aios.core only, no runtime/agent imports.
"""

from __future__ import annotations

import ast
import os
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# Re-use layer classification from guard to keep single source of truth.
from .guard import LAYER_KEYWORDS, classify_module


@dataclass
class ImportInfo:
    """Single import occurrence."""

    name: str
    line: int
    is_relative: bool = False
    is_dynamic: bool = False
    alias: Optional[str] = None


@dataclass
class CallInfo:
    """Function/method call occurrence."""

    func: str
    line: int
    args: List[str] = field(default_factory=list)


@dataclass
class InheritanceInfo:
    """Class inheritance occurrence."""

    class_name: str
    bases: List[str]
    line: int


@dataclass
class DecoratorInfo:
    """Decorator occurrence."""

    target: str  # function or class name
    decorator: str
    line: int


@dataclass
class ModuleScanResult:
    """Structured scan result for a single module."""

    file: str
    module_path: str
    layer: str
    imports: List[ImportInfo] = field(default_factory=list)
    calls: List[CallInfo] = field(default_factory=list)
    inheritances: List[InheritanceInfo] = field(default_factory=list)
    decorators: List[DecoratorInfo] = field(default_factory=list)
    has_parse_error: bool = False
    parse_error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "file": self.file,
            "module_path": self.module_path,
            "layer": self.layer,
            "imports": [{"name": i.name, "line": i.line, "is_relative": i.is_relative, "is_dynamic": i.is_dynamic} for i in self.imports],
            "calls": [{"func": c.func, "line": c.line} for c in self.calls],
            "inheritances": [{"class_name": h.class_name, "bases": h.bases, "line": h.line} for h in self.inheritances],
            "decorators": [{"target": d.target, "decorator": d.decorator, "line": d.line} for d in self.decorators],
            "has_parse_error": self.has_parse_error,
            "parse_error": self.parse_error,
        }


def _extract_imports(tree: ast.AST) -> List[ImportInfo]:
    imports: List[ImportInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportInfo(name=alias.name, line=node.lineno, alias=alias.asname))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            is_relative = node.level > 0
            # For relative imports without module, use alias names
            if not mod and is_relative:
                for alias in node.names:
                    imports.append(ImportInfo(name=f".{alias.name}", line=node.lineno, is_relative=True, alias=alias.asname))
            else:
                # Record the module being imported from
                target = mod if mod else ".".join(a.name for a in node.names)
                imports.append(ImportInfo(name=target, line=node.lineno, is_relative=is_relative))
                # Also record individual names for finer checks (e.g., from X import Y)
                for alias in node.names:
                    if alias.name != "*":
                        full = f"{mod}.{alias.name}" if mod else alias.name
                        # Avoid duplicate if mod already recorded and alias is submodule
                        if full != mod:
                            imports.append(ImportInfo(name=full, line=node.lineno, is_relative=is_relative, alias=alias.asname))
        # Dynamic imports: importlib.import_module, __import__, importlib.__import__
        elif isinstance(node, ast.Call):
            func_name = _get_call_name(node)
            if func_name in ("importlib.import_module", "import_module", "__import__", "importlib.__import__"):
                # Try to extract string argument
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    imports.append(ImportInfo(name=node.args[0].value, line=node.lineno, is_dynamic=True))
                elif node.args:
                    # Dynamic with non-constant arg -> UNKNOWN, mark as dynamic unknown
                    imports.append(ImportInfo(name="<dynamic>", line=node.lineno, is_dynamic=True))
    return imports


def _get_call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    elif isinstance(func, ast.Attribute):
        parts = []
        cur = func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return ""


def _extract_calls(tree: ast.AST) -> List[CallInfo]:
    calls: List[CallInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _get_call_name(node)
            if name:
                calls.append(CallInfo(func=name, line=node.lineno))
    return calls


def _extract_inheritance(tree: ast.AST) -> List[InheritanceInfo]:
    result: List[InheritanceInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(_get_call_name(ast.Call(func=base, args=[], keywords=[])) or ast.unparse(base) if hasattr(ast, "unparse") else str(base.attr))
                    # Fallback: try to get dotted name
                    try:
                        bases[-1] = ast.unparse(base)  # type: ignore
                    except Exception:
                        pass
                else:
                    try:
                        bases.append(ast.unparse(base))  # type: ignore
                    except Exception:
                        bases.append(str(type(base).__name__))
            result.append(InheritanceInfo(class_name=node.name, bases=bases, line=node.lineno))
    return result


def _extract_decorators(tree: ast.AST) -> List[DecoratorInfo]:
    result: List[DecoratorInfo] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for dec in node.decorator_list:
                try:
                    dec_name = ast.unparse(dec) if hasattr(ast, "unparse") else str(dec)  # type: ignore
                except Exception:
                    dec_name = getattr(dec, "id", str(type(dec).__name__))
                result.append(DecoratorInfo(target=node.name, decorator=dec_name, line=node.lineno))
    return result


def scan_source_extended(source_code: str, module_path: str = "<string>") -> ModuleScanResult:
    """Parse source and extract structured architecture info.

    Fail-closed: SyntaxError -> has_parse_error=True, not raised.
    Caller (gate) must treat parse_error as UNKNOWN -> FAIL.
    """
    layer = classify_module(module_path)
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        return ModuleScanResult(
            file=module_path,
            module_path=module_path,
            layer=layer,
            has_parse_error=True,
            parse_error=str(exc),
        )
    imports = _extract_imports(tree)
    calls = _extract_calls(tree)
    inheritances = _extract_inheritance(tree)
    decorators = _extract_decorators(tree)
    return ModuleScanResult(
        file=module_path,
        module_path=module_path,
        layer=layer,
        imports=imports,
        calls=calls,
        inheritances=inheritances,
        decorators=decorators,
    )


def scan_file(path: str) -> ModuleScanResult:
    """Scan a single file on disk."""
    if not path.endswith(".py"):
        return ModuleScanResult(file=path, module_path=path, layer=classify_module(path))
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        return ModuleScanResult(file=path, module_path=path, layer=classify_module(path), has_parse_error=True, parse_error=str(exc))
    return scan_source_extended(content, module_path=path)


def scan_directory(directory: str) -> List[ModuleScanResult]:
    """Recursively scan a directory for .py files."""
    results: List[ModuleScanResult] = []
    for root, _dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(".py"):
                results.append(scan_file(os.path.join(root, name)))
    return results


def enumerate_files(roots: List[str]) -> List[str]:
    """Enumerate all .py files under given roots."""
    files: List[str] = []
    for root in roots:
        p = pathlib.Path(root)
        if p.is_file() and p.suffix == ".py":
            files.append(str(p))
        elif p.is_dir():
            for py in p.rglob("*.py"):
                files.append(str(py))
    return files


__all__ = [
    "ImportInfo",
    "CallInfo",
    "InheritanceInfo",
    "DecoratorInfo",
    "ModuleScanResult",
    "scan_source_extended",
    "scan_file",
    "scan_directory",
    "enumerate_files",
]
